import os
import random

import paddle
import pandas as pd
import pickle
import datetime
from sklearn.preprocessing import StandardScaler

from WPF.models import ForecastTask, TurbineData


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


def to_unix_time(dt):
    # timestamp to unix
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())


def from_unix_time(unix_time):
    # unix to timestamp
    return datetime.datetime.utcfromtimestamp(unix_time)


class TSPredDataset(paddle.io.Dataset):
    """时序Pred DataSet
    划分数据集、适配dataloader所需的dataset格式
    ref: https://github.com/thuml/Autoformer/blob/main/data_provider/data_loader.py
    """

    def __init__(self, data,
                 ts_col='DATATIME',
                 use_cols=['WINDSPEED', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY',
                           'PRESSURE'],
                 known_cols=['WINDSPEED', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY', 'PRESSURE'],
                 labels=['YD15'],
                 input_len=1, pred_len=1):
        super(TSPredDataset, self).__init__()
        self.ts_col = ts_col  # 时间戳列
        self.use_cols = use_cols  # 训练时使用的特征列
        self.known_cols = known_cols  # 预测时未来已知的特征列
        self.labels = labels  # 待预测的标签列
        self.input_len = input_len  # 模型输入数据的样本点长度，15分钟间隔，一个小时14个点，近5天的数据就是24*4*5
        self.pred_len = pred_len  # 预测长度，预测次日00:00至23:45实际功率，即1天：24*4
        # 由于赛题要求利用当日05:00之前的数据，预测次日00:00至23:45实际功率
        # 所以x和label要间隔19*4个点
        self.scale = True  # 是否需要标准化

        self.transform(data)

    def transform(self, df):
        # 获取unix时间戳、输入特征和预测标签
        time_stamps, x_values, y_values, future_values = df[self.ts_col].apply(lambda x: to_unix_time(x)).values, df[
            self.use_cols].values, df[self.labels].values, df[self.known_cols].values
        # 截取边界
        border1 = 0
        border2 = len(df)

        # 标准化
        self.scaler = StandardScaler()
        if self.scale:
            # 读取预训练好的scaler
            self.x_scaler = pickle.load(open(os.path.join(model_path, 'x_scaler.pkl'), 'rb'))
            self.y_scaler = pickle.load(open(os.path.join(model_path, 'y_scaler.pkl'), 'rb'))

            x_data = self.x_scaler.transform(x_values)
            y_data = self.y_scaler.transform(y_values)
        else:
            x_data = x_values
            y_data = y_values
            future_data = future_values

        # array to paddle tensor
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
        r_begin = s_begin
        r_end = s_end

        # TODO 可以增加对未来可见数据的获取
        seq_x = self.data_x[s_begin:s_end]
        seq_y = self.data_y[r_begin:r_end]
        ts_x = self.time_stamps[s_begin:s_end]
        ts_y = self.time_stamps[r_begin:r_end]
        return seq_x, seq_y, ts_x, ts_y

    def __len__(self):
        """
        实现__len__方法，返回数据集总数目
        """
        return len(self.data_x)


def data_preprocess(df):
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

    # ===========重采样（可选） + 线性插值===========
    df = df.set_index('DATATIME')
    # 重采样（可选）：比如04风机缺少2022-04-10和2022-07-25两天的数据，重采样会把这两天数据补充进来
    # df = df.resample(rule=to_offset('15T').freqstr, label='right', closed='right').interpolate(method='linear', limit_direction='both').reset_index()
    # TODO 尝试一些其他缺失值处理方式，比如，用同时刻附近风机的值求均值填补缺失值
    df = df.interpolate(method='linear', limit_direction='both').reset_index()
    print('After Resampling:', df.shape)

    # ===========异常值处理===========
    # 当实际风速为0时，功率置为0
    df.loc[df['ROUND(A.WS,1)'] == 0, 'YD15'] = 0

    df.drop(columns=['PREPOWER',
                     'ROUND(A.POWER,0)'], axis=0, inplace=True)
    # TODO 风速过大但功率为0的异常：先设计函数拟合出：实际功率=f(风速)，
    # 然后代入异常功率的风速获取理想功率，替换原异常功率

    # TODO 对于在特定风速下的离群功率（同时刻用IQR检测出来），做功率修正（如均值修正）
    return df


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


def forecast(df):
    # 数据预处理
    df = data_preprocess(df)
    # 特征工程
    # 准备数据加载器
    input_len = 1
    pred_len = 1
    pred_dataset = TSPredDataset(df, input_len=input_len, pred_len=pred_len)
    pred_loader = paddle.io.DataLoader(pred_dataset, shuffle=False, batch_size=1, drop_last=False)
    # 定义模型
    mlp = MLP()
    # 导入模型权重文件
    mlp.set_state_dict(paddle.load(os.path.join(model_path, 'mlp.pdparams')))
    mlp.eval()

    apower = []
    yd15 = []
    ts_y = []
    x_values = [[], [], [], [], []]
    pre_output = None

    x_scaler = pickle.load(open(os.path.join(model_path, 'x_scaler.pkl'), 'rb'))
    y_scaler = pickle.load(open(os.path.join(model_path, 'y_scaler.pkl'), 'rb'))

    index = 0

    for batch_id, data in enumerate(pred_loader()):
        x = data[0]
        tx_y = data[3]
        index = index + 1
        # 预测
        output = mlp(x)
        output = paddle.reshape(output, [output.shape[0], 1])
        output = y_scaler.inverse_transform(output)
        output = paddle.to_tensor(output, dtype='float32')
        output = paddle.reshape(output, [output.shape[0], 1, 1])

        forecastTask = ForecastTask.objects.filter(id=task_id)
        forecastTask = forecastTask[0]
        forecastTask.task_status = "预测中..." + str(int(index / data_length * 100)) + "%"
        forecastTask.save()

        apower.append(output.numpy().squeeze())
        yd15.append(output.numpy().squeeze())
        ts_y.append(from_unix_time(tx_y.numpy().squeeze()))

        x = paddle.reshape(x, [x.shape[0], 5])
        x = x_scaler.inverse_transform(x)
        x = x.squeeze()
        for index in range(0, len(x)):
            x_values[index].append(x[index])

    result = pd.DataFrame({'DATATIME': ts_y, 'WINDSPEED': x_values[0], 'WINDDIRECTION': x_values[1],
                           'TEMPERATURE': x_values[2], 'HUMIDITY': x_values[3], 'PRESSURE': x_values[4],
                           'YD15': yd15})
    # 将YD15小于0的值置为-128
    result.loc[result['YD15'] < 0, 'YD15'] = -128

    result = result[['DATATIME','WINDSPEED', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY', 'PRESSURE', 'YD15']]
    result.to_csv(result_path, index=False)


global model_path
global data_path
global start_time
global end_time
global task_id
global turbine_id
global result_path
global data_length


def start_predict(set_task_id, set_turbine_id, set_model_path, set_data_path, set_start_time, set_end_time):
    global model_path
    global data_path
    global start_time
    global end_time
    global task_id
    global turbine_id
    global result_path
    global data_length

    model_path = set_model_path
    data_path = set_data_path
    start_time = set_start_time
    end_time = set_end_time
    task_id = set_task_id
    turbine_id = set_turbine_id

    result_path = os.path.join("data", turbine_id, "result")
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    result_path = os.path.join(result_path, task_id + "result.csv")

    df = pd.read_csv(data_path,
                     parse_dates=['DATATIME'],
                     )

    df = df[(df['DATATIME'] >= start_time) & (df['DATATIME'] <= end_time)]
    data_length = len(df)

    # 预测结果
    forecast(df)

    currentTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    forecastTask = ForecastTask.objects.filter(id=task_id)
    forecastTask = forecastTask[0]
    forecastTask.task_status = "任务完成"
    forecastTask.task_finishTime = currentTime

    turbineData = TurbineData()
    turbineData.turbine_id = turbine_id
    turbineData.data_path = result_path
    turbineData.data_startTime = start_time
    turbineData.data_endTime = end_time
    turbineData.data_name = task_id + "result.csv"
    turbineData.data_type = "result"
    turbineData.data_size = get_readable_file_size(result_path)
    turbineData.data_uploadTime = currentTime
    turbineData.save()

    turbineData = TurbineData.objects.filter(data_name=task_id + "result.csv")
    result_id = turbineData[0].id

    forecastTask.result_id = result_id

    forecastTask.save()


def realtime_predict(realtimeData, modelPath):
    global model_path
    model_path = modelPath
    df = realtimeData
    # 特征工程
    # 准备数据加载器
    input_len = 1
    pred_len = 1
    pred_dataset = TSPredDataset(df, input_len=input_len, pred_len=pred_len)
    pred_loader = paddle.io.DataLoader(pred_dataset, shuffle=False, batch_size=1, drop_last=False)
    # 定义模型
    mlp = MLP()
    # 导入模型权重文件
    mlp.set_state_dict(paddle.load(os.path.join(modelPath, 'mlp.pdparams')))
    mlp.eval()

    apower = []
    yd15 = []
    ts_y = []
    x_values = [[], [], [], [], []]
    pre_output = None

    x_scaler = pickle.load(open(os.path.join(modelPath, 'x_scaler.pkl'), 'rb'))
    y_scaler = pickle.load(open(os.path.join(modelPath, 'y_scaler.pkl'), 'rb'))

    index = 0

    for batch_id, data in enumerate(pred_loader()):
        x = data[0]
        tx_y = data[3]
        index = index + 1
        # 预测
        output = mlp(x)
        output = paddle.reshape(output, [output.shape[0], 1])
        output = y_scaler.inverse_transform(output)
        output = paddle.to_tensor(output, dtype='float32')
        output = paddle.reshape(output, [output.shape[0], 1, 1])

        apower.append(output.numpy().squeeze())
        yd15.append(output.numpy().squeeze())
        ts_y.append(from_unix_time(tx_y.numpy().squeeze()))

        x = paddle.reshape(x, [x.shape[0], 5])
        x = x_scaler.inverse_transform(x)
        x = x.squeeze()
        for index in range(0, len(x)):
            x_values[index].append(x[index])

    result = pd.DataFrame({'DATATIME': ts_y, 'WINDSPEED': x_values[0], 'WINDDIRECTION': x_values[1],
                           'TEMPERATURE': x_values[2], 'HUMIDITY': x_values[3], 'PRESSURE': x_values[4],
                           'YD15': yd15})

    result = result[['DATATIME', 'WINDSPEED', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY', 'PRESSURE', 'YD15']]

    # 将YD15小于0的值置为-128
    result.loc[result['YD15'] < 0, 'YD15'] = -128

    randomFileName = str(random.randint(0, 1000000)) + ".csv"
    result.to_csv(randomFileName, index=False)

    df = pd.read_csv(randomFileName,
                     parse_dates=['DATATIME'])
    os.remove(randomFileName)
    currentTime = datetime.datetime.now()
    # startTime设置为离当前时间最近的15分钟的整点时间
    if currentTime.minute < 15:
        startTime = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    elif (currentTime.minute < 30):
        startTime = datetime.datetime.now().replace(minute=15, second=0, microsecond=0)
    elif (currentTime.minute < 45):
        startTime = datetime.datetime.now().replace(minute=30, second=0, microsecond=0)
    else:
        startTime = datetime.datetime.now().replace(minute=45, second=0, microsecond=0)
    # 将一天的时间，以15分钟为间隔，分成96个时间片
    time_list = []
    for i in range(0, 96):
        time_list.append(startTime + datetime.timedelta(minutes=15 * i))
    # 将预测结果的DATATIME列设为时间片
    df['DATATIME'] = time_list
    return df
