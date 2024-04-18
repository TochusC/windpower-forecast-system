import os
import datetime
import pickle
import paddle
import pandas as pd
from pandas.tseries.frequencies import to_offset
import numpy as np
import paddle.nn.functional as F
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler


from WPF.models import ForecastModel


# 随机种子，保证实验能复现
import random

import warnings

warnings.filterwarnings('ignore')


def data_preprocess(df, isError=False):
    """数据预处理：
        1、读取数据
        2、数据排序
        3、去除重复值
        4、重采样（可选）
        5、缺失值处理
        6、异常值处理
    """
    # ===========读取数据===========
    df = df.sort_values(by='DATATIME', ascending=True)
    print('df.shape:', df.shape)
    print(f"Time range from {df['DATATIME'].values[0]} to {df['DATATIME'].values[-1]}")

    # ===========去除重复值===========
    df = df.drop_duplicates(subset='DATATIME', keep='first')
    print('After Dropping dulicates:', df.shape)
    # ============去除双空============
    print('Before Dropping NA:', df.shape)
    # 将YD15若为空值，则用ROUND(A.POWER, 0)代替
    if isError:
        df = df.dropna(subset=['YD15'])
    df.loc[df['YD15'].isnull(), 'YD15'] = df.loc[df['YD15'].isnull(), 'ROUND(A.POWER,0)']
    df = df.dropna(subset=['YD15'])
    print('After Dropping NA:', df.shape)
    # ===========剔除异常值=============
    print('Before Deleting Stange:', df.shape)
    columns = ['YD15', 'ROUND(A.POWER,0)', 'ROUND(A.WS,1)', 'WINDSPEED']
    status = True
    while (status):
        firstLen = len(df)
        status = False

        std = df.std()
        mean = df.mean()
        max_threshold = mean + 4 * std
        min_threshold = mean - 4 * std
        for column in columns:
            df.drop(df[df.loc[:, column] > max_threshold[column]].index, inplace=True)
            df.drop(df[df.loc[:, column] < min_threshold[column]].index, inplace=True)
        if firstLen != len(df):
            status = True
    print('After Deleting Stange:', df.shape)
    # ===========异常值处理===========
    # 当实际风速为0时，功率置为0
    df.loc[df['ROUND(A.WS,1)'] == 0, 'YD15'] = 0

    # ===========空值处理===========
    df.drop(columns=['PREPOWER', 'ROUND(A.WS,1)',
                     'ROUND(A.POWER,0)'], axis=0, inplace=True)
    df.dropna(inplace=True)
    print('Before Resampling:', df.shape)
    df = df.set_index('DATATIME')
    df = df.resample('15T').fillna(method='ffill').reset_index()
    df = df.fillna(method='ffill').reset_index()
    print('After Resampling:', df.shape)

    return df


class EarlyStopping():
    """早停
    当验证集超过patience个epoch没有出现更好的评估分数，及早终止训练
    若当前epoch表现超过历史最佳分数，保存该节点模型
    参考：https://blog.csdn.net/m0_63642362/article/details/121244655
    """

    def __init__(self, patience=16, verbose=False, delta=0,
                 ckp_save_path='/home/aistudio/submission/model/model_checkpoint_windid_04.pdparams'):
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.ckp_save_path = ckp_save_path

    def __call__(self, val_loss, model):
        print("val_loss={}".format(val_loss))
        score = -val_loss
        # 首轮，直接更新best_score和保存节点模型
        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        # 若当前epoch表现没超过历史最佳分数，且累积发生次数超过patience，早停
        elif score < self.best_score + self.delta:
            self.counter += 1
            print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        # 若当前epoch表现超过历史最佳分数，更新best_score，保存该节点模型
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        # 保存模型
        if self.verbose:
            print(
                f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
        paddle.save(model.state_dict(), self.ckp_save_path)
        self.val_loss_min = val_loss


# unix时间戳转换
def to_unix_time(dt):
    # timestamp to unix
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())


def from_unix_time(unix_time):
    # unix to timestamp
    return datetime.datetime.utcfromtimestamp(unix_time)


class TSDataset(paddle.io.Dataset):
    """时序DataSet
    划分数据集、适配dataloader所需的dataset格式
    ref: https://github.com/thuml/Autoformer/blob/main/data_provider/data_loader.py
    """

    def __init__(self, data,
                 ts_col='DATATIME',
                 use_cols=['WINDSPEED', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY',
                           'PRESSURE', ],
                 labels=['YD15'],
                 input_len=1, pred_len=1, data_type='train',
                 train_ratio=0.8, val_ratio=0.1):
        super(TSDataset, self).__init__()
        self.ts_col = ts_col  # 时间戳列
        self.use_cols = use_cols  # 训练时使用的特征列
        self.labels = labels  # 待预测的标签列
        self.input_len = input_len  # 模型输入数据的样本点长度，15分钟间隔，一个小时14个点，近5天的数据就是24*4*5
        self.pred_len = pred_len  # 预测长度，预测次日00:00至23:45实际功率，即1天：24*4
        self.data_type = data_type  # 需要加载的数据类型
        self.scale = True  # 是否需要标准化
        self.train_ratio = train_ratio  # 训练集划分比例
        self.val_ratio = val_ratio  # 验证集划分比例
        assert data_type in ['train', 'val', 'test']  # 确保data_type输入符合要求
        type_map = {'train': 0, 'val': 1, 'test': 2}
        self.set_type = type_map[self.data_type]

        self.transform(data)

    def transform(self, df):
        # 获取unix时间戳、输入特征和预测标签
        time_stamps, x_values, y_values = df[self.ts_col].apply(lambda x: to_unix_time(x)).values, df[
            self.use_cols].values, df[self.labels].values
        # 划分数据集
        # 这里可以按需设置划分比例
        num_train = int(len(df) * self.train_ratio)
        num_vali = int(len(df) * self.val_ratio)
        num_test = len(df) - num_train - num_vali
        border1s = [0, num_train - self.input_len, len(df) - num_test - self.input_len]
        border2s = [num_train, num_train + num_vali, len(df)]
        # 获取data_type下的左右数据截取边界
        border1 = border1s[self.set_type]
        border2 = border2s[self.set_type]

        # 标准化
        self.x_scaler = StandardScaler()
        self.y_scaler = StandardScaler()
        if self.scale:
            # 使用训练集得到scaler对象
            train_data_x = x_values[border1s[0]:border2s[0]]
            train_data_y = y_values[border1s[0]:border2s[0]]

            self.x_scaler.fit(train_data_x)
            self.y_scaler.fit(train_data_y)

            x_data = self.x_scaler.transform(x_values)
            y_data = self.y_scaler.transform(y_values)

            # 保存scaler
            pickle.dump(self.x_scaler, open(os.path.join(model_dir, "x_scaler.pkl"), 'wb'))
            pickle.dump(self.y_scaler, open(os.path.join(model_dir, "y_scaler.pkl"), 'wb'))
        else:
            x_data = x_values
            y_data = y_values

        # array to forecast tensor
        self.time_stamps = paddle.to_tensor(time_stamps[border1:border2], dtype='int64')
        self.data_x = paddle.to_tensor(x_data[border1:border2], dtype='float32')
        self.data_y = paddle.to_tensor(y_data[border1:border2], dtype='float32')

    def __getitem__(self, index):
        """
        实现__getitem__方法，定义指定index时如何获取数据，并返回单条数据（训练数据）
        """
        # 由于赛题要求利用当日05:00之前的数据，预测次日00:00至23:45实际功率
        # 所以x和label要间隔19*4个点
        s_begin = index
        s_end = s_begin + self.input_len

        seq_x = self.data_x[s_begin:s_end]
        seq_y = self.data_y[s_begin:s_end]
        ts_x = self.time_stamps[s_begin:s_end]
        ts_y = self.time_stamps[s_begin:s_end]

        return seq_x, seq_y, ts_x, ts_y

    def __len__(self):
        """
        实现__len__方法，返回数据集总数目
        """
        return len(self.data_x) - self.input_len + 1


# only move one step of LSTM,
# the recurrent loop is implemented inside training loop
class MLP(paddle.nn.Layer):
    def __init__(self, feat_num=5, hidden_size=512, dropout_rate=0.2):
        super(MLP, self).__init__()
        self.proj = paddle.nn.Linear(in_features=feat_num, out_features=hidden_size)
        self.relu1 = paddle.nn.ReLU()
        self.linear1 = paddle.nn.Linear(in_features=hidden_size, out_features=hidden_size // 2)
        self.linear2 = paddle.nn.Linear(in_features=hidden_size // 2, out_features=1)
        self.dropout = paddle.nn.Dropout(dropout_rate)

    def forward(self, x):
        x = self.proj(x)
        x = self.relu1(x)
        x = self.dropout(x)
        output = x
        output = self.linear1(output)
        output = self.dropout(output)
        output = self.linear2(output)

        return output


class MSELoss(paddle.nn.Layer):
    """
    设置损失函数, 多任务模型，两个任务MSE的均值做loss输出
    """

    def __init__(self):
        super(MSELoss, self).__init__()

    def forward(self, inputs, labels):
        mse_loss = paddle.nn.loss.MSELoss()
        mse = mse_loss(inputs, labels[:, ].squeeze(-1))
        # TODO 也可以自行设置各任务的权重，让其更偏好YD15
        # 即让多任务有主次之分
        return mse


def calc_acc(y_true, y_pred):
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    return 1 - rmse / 201000


def train(df):
    # 设置数据集
    train_dataset = TSDataset(df, data_type='train')
    val_dataset = TSDataset(df, data_type='val')
    test_dataset = TSDataset(df, data_type='test')
    print(f'LEN | train_dataset:{len(train_dataset)}, val_dataset:{len(val_dataset)}, test_dataset:{len(test_dataset)}')

    # 设置数据读取器
    train_loader = paddle.io.DataLoader(train_dataset, shuffle=True, batch_size=batch_size, drop_last=True)
    val_loader = paddle.io.DataLoader(val_dataset, shuffle=False, batch_size=batch_size, drop_last=True)
    test_loader = paddle.io.DataLoader(test_dataset, shuffle=False, batch_size=1, drop_last=False)

    # 设置模型
    mlp = MLP()
    if os.path.exists(os.path.join(model_dir, 'mlp.pdparams')):
        mlp.set_state_dict(paddle.load(os.path.join(model_dir, 'mlp.pdparams')))
    # 设置优化器
    scheduler = paddle.optimizer.lr.ReduceOnPlateau(learning_rate=learning_rate, factor=0.5, patience=3, verbose=True)
    opt = paddle.optimizer.Adam(learning_rate=scheduler, parameters=mlp.parameters())

    # 设置损失
    mse_loss = MSELoss()

    train_loss = []
    valid_loss = []
    train_epochs_loss = []
    valid_epochs_loss = []
    decoder_early_stopping = EarlyStopping(patience=patience, verbose=True,
                                           ckp_save_path=os.path.join(model_dir, 'mlp.pdparams'))

    for epoch in tqdm(range(epoch_num)):
        # =====================train============================
        forecastModel = ForecastModel.objects.filter(id=model_id)
        forecastModel = forecastModel[0]
        forecastModel.model_status = '训练中...' + str(int(epoch/epoch_num*100 * current_data_num / data_num)) + '%'
        forecastModel.save()
        train_epoch_loss, train_epoch_mse = [], []
        mlp.train()  # 开启训练
        for batch_id, data in enumerate(train_loader()):
            x = data[0]
            y = data[1]
            ts_x = data[2]
            tx_y = data[3]
            # 预测
            outputs = mlp(x)
            outputs = paddle.reshape(outputs, [outputs.shape[0], -1])

            # 计算损失
            mse = mse_loss(outputs, y)
            # 反向传播
            mse.backward()
            # 梯度下降
            opt.step()
            # 清空梯度
            opt.clear_grad()
            train_epoch_loss.append(mse.numpy()[0])
            train_loss.append(mse.item())
            train_epoch_mse.append(mse.item())
        train_epochs_loss.append(np.average(train_epoch_loss))
        print("epoch={}/{} of train | loss={}, MSE of YD15:{} ".format(epoch, epoch_num,
                                                                       np.average(
                                                                           train_epoch_loss),
                                                                       np.average(
                                                                           train_epoch_mse)))

        # =====================valid============================
        mlp.eval()
        valid_epoch_loss, valid_epochs_mse = [], []
        for batch_id, data in enumerate(val_loader()):
            x = data[0]
            y = data[1]
            ts_x = data[2]
            tx_y = data[3]

            # 预测
            outputs = mlp(x)
            outputs = paddle.reshape(outputs, [outputs.shape[0], -1])
            # 计算损失
            mse = mse_loss(outputs, y)
            valid_epoch_loss.append(mse.numpy()[0])
            valid_loss.append(mse.numpy()[0])
            valid_epochs_mse.append(mse.item())
        valid_epochs_loss.append(np.average(valid_epoch_loss))
        print('Valid:MSE of YD15:{}'.format(np.average(valid_epochs_mse)))

        # ==================early stopping======================
        decoder_early_stopping(valid_epochs_loss[-1], model=mlp)
        if decoder_early_stopping.early_stop:
            print(f"Early stopping at Epoch {epoch - patience}")
            break
    # =====================test============================
    # 加载最优epoch节点下的模型
    mlp = MLP()
    mlp.set_state_dict(paddle.load(os.path.join(model_dir, 'mlp.pdparams')))
    # 开启评估/预测
    mlp.eval()
    test_loss, test_epoch_mse = [], []
    test_acc = []
    for batch_id, data in tqdm(enumerate(test_loader())):
        x = data[0]
        y = data[1]
        ts_x = data[2]
        tx_y = data[3]

        # 预测
        outputs = mlp(x)
        outputs = paddle.reshape(outputs, [outputs.shape[0], -1])

        # 计算损失
        mse = mse_loss(outputs, y)
        acc = calc_acc(y.numpy().squeeze(0)[:, :], outputs.numpy().squeeze(0))
        test_loss.append(mse.numpy()[0])
        test_epoch_mse.append(mse.numpy()[0])
        test_acc.append(acc)

    print('Test: ')
    print('MSE of YD15:{}'.format(np.average(test_epoch_mse)))
    print('Mean MSE:', np.mean(test_loss))
    print('ACC of YD15:{}'.format(np.average(test_acc)))


def get_readable_file_size(file_path):
    # 获取文件大小
    file_size = os.path.getsize(file_path)

    # 定义文件大小单位
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']

    # 迭代计算文件大小单位
    size_index = 0
    while file_size > 1024 and size_index < len(size_units) - 1:
        file_size /= 1024
        size_index += 1

    # 格式化文件大小
    file_size = round(file_size, 2)
    readable_size = f'{file_size} {size_units[size_index]}'

    return readable_size


def start_train(data_path_list, model_id_now, isError=False):
    debug = True
    global model_id
    global turbine_id
    global model_dir
    global data_num
    global current_data_num

    model_id = model_id_now

    forecastModel = ForecastModel.objects.filter(id=model_id)
    forecastModel = forecastModel[0]
    turbine_id = forecastModel.turbine_id

    model_dir = os.path.join('model', str(turbine_id), "mlp", str(model_id))
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    data_num = len(data_path_list)
    for data_path in data_path_list:
        current_data_num += 1
        df = pd.read_csv(os.path.join(data_path),
                         parse_dates=['DATATIME'],
                         infer_datetime_format=True,
                         dayfirst=True,
                         )
        df['DATATIME'] = pd.to_datetime(df['DATATIME'])
        print(f'turbine_id:{turbine_id}')

        if debug:
            df = df.iloc[-24 * 4 * 200:, :]

        df = data_preprocess(df, isError=True)
        # 特征工程
        # 训练模型
        train(df)
        print(f'turbine_id:{turbine_id}')
        print("----------------------------------------")

    forecastModel = ForecastModel.objects.filter(id=model_id)
    forecastModel = forecastModel[0]
    forecastModel.model_status = "准备就绪"
    forecastModel.model_path = model_dir
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    forecastModel.model_trainTime = current_time
    forecastModel.model_size = get_readable_file_size(os.path.join(model_dir, "mlp.pdparams"))
    forecastModel.save()

model_dir = ""
model_id = ""
turbine_id = ""
input_len = 1  # 输入序列的长度为 120*4
pred_len = 1  # 预测序列的长度为 24*4
epoch_num = 16  # 模型训练的轮数
batch_size = 512  # 每个训练批次使用的样本数量
learning_rate = 0.005  # 学习率
patience = 16  # 如果连续patience个轮次性能没有提升，就会停止训练。
data_num = 0
current_data_num = 0