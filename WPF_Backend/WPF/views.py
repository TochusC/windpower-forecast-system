import json
import os.path
import random
import re
import subprocess

import openai
import psutil

import pandas as pd
from datetime import datetime
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from forecast.train import mlp as train_mlp
from forecast.predict import mlp as predict_mlp
from forecast.train import gcn_lstm as train_gcn_lstm
from forecast.predict import gcn_lstm as predict_gcn_lstm
from forecast.train import gcn_lstm_mlp as train_gcn_lstm_mlp
from forecast.predict import gcn_lstm_mlp as predict_gcn_lstm_mlp

from WPF.models import Turbine, TurbineData, ForecastModel, ForecastTask, WebsiteStatistics, GuestBook

startTime = datetime.now().timestamp()


def delete_path(path):
    if os.path.isfile(path):
        # 如果是文件，则直接删除
        os.remove(path)
    elif os.path.isdir(path):
        # 如果是目录，则递归删除目录下所有文件和子目录
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir_ in dirs:
                dir_path = os.path.join(root, dir_)
                delete_path(dir_path)
        # 删除目录本身
        os.rmdir(path)


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


@require_http_methods(["GET"])
def get_turbine(request):
    turbine = Turbine.objects.filter()
    turbine_json = serializers.serialize("json", turbine)
    turbine_dict = json.loads(turbine_json)
    return JsonResponse(turbine_dict, safe=False)


@require_http_methods(["POST"])
def add_turbine(request):
    turbine_id = request.POST.get("turbine_id")
    turbine_name = request.POST.get("turbine_name")
    turbine_comment = request.POST.get("turbine_comment")
    turbine_status = "正常"
    turbine = Turbine(turbine_id=turbine_id, turbine_name=turbine_name,
                      turbine_comment=turbine_comment, turbine_status=turbine_status, )

    model_type_string = request.POST.get("model_type")
    model_type_list = model_type_string.split(",")
    for model_type in model_type_list:
        if model_type == "":
            continue
        forecastModel = ForecastModel(turbine_id=turbine_id, model_type=model_type, model_data="", model_size="",
                                      model_path="", model_status="未选择数据", model_comment="", model_trainTime="")
        forecastModel.save()

    turbine.save()

    websiteStatistics = WebsiteStatistics.objects.first()
    websiteStatistics.statistics_uploadTurbine += 1

    global startTime
    currentTime = datetime.now().timestamp()
    websiteStatistics.statistics_time += currentTime - startTime

    startTime = currentTime

    websiteStatistics.save()

    return JsonResponse({"status": "success"})


def delete_task_file(turbine_id, task_id):
    if task_id == "all":
        forecastTask = ForecastTask.objects.filter(turbine_id=turbine_id)
    else:
        forecastTask = ForecastTask.objects.filter(id=task_id)
    for task in forecastTask:
        if task.task_status == "任务完成":
            data_id = task.result_id
            data = TurbineData.objects.filter(id=data_id)
            for d in data:
                delete_path(d.data_path)
                d.delete()
    forecastTask.delete()


@require_http_methods(["POST"])
def delete_turbine(request):
    turbine_id = request.POST.get("turbine_id")

    turbine = Turbine.objects.filter(turbine_id=turbine_id)
    turbine.delete()
    delete_data_file(turbine_id, "all", "all")
    delete_path(os.path.join("data", turbine_id))
    delete_model_file(turbine_id, "all")
    delete_path(os.path.join("model", turbine_id))
    delete_task_file(turbine_id, "all")
    return JsonResponse({"status": "success"})


@require_http_methods(["POST"])
def upload_data(request):
    fileType = request.POST.get("data_type")
    turbineID = request.POST.get("turbine_id")
    uploaded_file = request.FILES.get("file")
    data_comment = request.POST.get("data_comment")

    dataPath = os.path.join("data", turbineID, fileType)

    if not os.path.exists(dataPath):
        os.makedirs(dataPath)

    dataPath = os.path.join(dataPath, uploaded_file.name)
    with open(dataPath, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    fileSize = get_readable_file_size(dataPath)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if fileType == "train":
        df = pd.read_csv(dataPath, parse_dates=['DATATIME'],
                         dayfirst=True)
    else:
        df = pd.read_csv(dataPath, parse_dates=['DATATIME'])

    data_startTime = df['DATATIME'][0]
    data_endTime = df['DATATIME'][len(df) - 1]

    turbineData = TurbineData(turbine_id=turbineID, data_path=dataPath, data_name=uploaded_file.name
                              , data_type=fileType, data_uploadTime=current_time, data_size=fileSize,
                              data_comment=data_comment, data_startTime=data_startTime, data_endTime=data_endTime)
    turbineData.save()

    websiteStatistics = WebsiteStatistics.objects.first()
    websiteStatistics.statistics_upload += 1

    global startTime

    currentTime = datetime.now().timestamp()
    websiteStatistics.statistics_time += currentTime - startTime

    startTime = currentTime

    websiteStatistics.save()

    return JsonResponse({"status": "success"})


def delete_data_file(turbineID, fileType, fileName):
    isFile = False
    if fileType == "all":
        turbineData = TurbineData.objects.filter(turbine_id=turbineID)
        dataPath = os.path.join("data", turbineID)
    elif fileName == "all":
        turbineData = TurbineData.objects.filter(turbine_id=turbineID, data_type=fileType)
        dataPath = os.path.join("data", turbineID, fileType)
    else:
        turbineData = TurbineData.objects.filter(turbine_id=turbineID, data_type=fileType, data_name=fileName)
        dataPath = os.path.join("data", turbineID, fileType, fileName)

    turbineData.delete()
    delete_path(dataPath)


@require_http_methods(["POST"])
def delete_data(request):
    dataID = request.POST.get("data_id")
    turbineData = TurbineData.objects.filter(id=dataID)
    turbineData_json = serializers.serialize("json", turbineData)
    turbineData_Dict = json.loads(turbineData_json)

    for data in turbineData_Dict:
        turbineID = data["fields"]["turbine_id"]
        fileType = data["fields"]["data_type"]
        fileName = data["fields"]["data_name"]
        delete_data_file(turbineID, fileType, fileName)

    turbineData.delete()

    return JsonResponse({"status": "success"})


@require_http_methods(["GET"])
def get_turbineData(request):
    turbine_id = request.GET.get("turbine_id")
    data_type = request.GET.get("data_type")

    if not turbine_id:
        turbine_id = "all"
    if not data_type:
        data_type = "all"

    if turbine_id == "all":
        if data_type == "all":
            turbineData = TurbineData.objects.filter()
        else:
            turbineData = TurbineData.objects.filter(data_type=data_type)
    else:
        if data_type == "all":
            turbineData = TurbineData.objects.filter(turbine_id=turbine_id)
        else:
            turbineData = TurbineData.objects.filter(turbine_id=turbine_id, data_type=data_type)

    turbineData_json = serializers.serialize("json", turbineData)
    turbineData_dict = json.loads(turbineData_json)
    return JsonResponse(turbineData_dict, safe=False)


def add_forecastModel(request):
    turbineID = request.POST.get("turbine_id")
    modelType = request.POST.get("model_type")
    modelComment = request.POST.get("model_comment")
    modelData = request.POST.get("model_data")

    modelStatus = "待训练"

    forecastModel = ForecastModel(turbine_id=turbineID, model_type=modelType,
                                  model_comment=modelComment, model_data=modelData,
                                  model_status=modelStatus)
    forecastModel.save()

    return JsonResponse({"status": "success"})

@require_http_methods(["POST"])
def alter_forecastModel(request):
    model_id = request.POST.get("model_id")
    modelData = request.POST.get("model_data")

    modelStatus = "待训练"

    forecastModel = ForecastModel.objects.filter(id=model_id)
    forecastModel.update(model_data=modelData, model_status=modelStatus)
    forecastModel = forecastModel[0]
    forecastModel.save()

    return JsonResponse({"status": "success"})


def delete_model_file(turbineID, modelID):
    if modelID == "all":
        forecastModel = ForecastModel.objects.filter(turbine_id=turbineID)
        dataPath = os.path.join("model", turbineID)
    else:
        forecastModel = ForecastModel.objects.filter(id=modelID)
        dataPath = os.path.join("model", turbineID, forecastModel[0].model_type, modelID)

    forecastModel.delete()
    delete_path(dataPath)

    return JsonResponse({"status": "success"})


@require_http_methods(["POST"])
def download_data(request):
    # 根据文件ID获取文件对象或检查文件的存在性
    data_id = request.POST.get('data_id')
    turbineData = TurbineData.objects.get(id=data_id)
    # 定义要下载的文件路径
    data_path = turbineData.data_path
    # 打开文件流，以二进制模式读取文件内容
    with open(data_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')

    # 设置文件名和Content-Disposition标头，指示为下载
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(data_id)

    websiteStatistics = WebsiteStatistics.objects.first()
    websiteStatistics.statistics_download += 1

    global startTime
    currentTime = datetime.now().timestamp()

    websiteStatistics.statistics_time += currentTime - startTime

    startTime = currentTime

    websiteStatistics.save()
    # 返回响应对象
    return response


@require_http_methods(["GET"])
def get_forecastModel(request):
    turbine_id = request.GET.get("turbine_id")
    model_id = request.GET.get("model_id")

    if turbine_id == "all" and model_id == "all":
        turbineModel = ForecastModel.objects.filter()
    else:
        if turbine_id == "all":
            turbineModel = ForecastModel.objects.filter(id=model_id)
        elif model_id == "all":
            turbineModel = ForecastModel.objects.filter(turbine_id=turbine_id)
        else:
            turbineModel = ForecastModel.objects.filter(turbine_id=turbine_id, id=model_id)

    turbineModel = serializers.serialize("json", turbineModel)
    turbineModel = json.loads(turbineModel)

    return JsonResponse(turbineModel, safe=False)


@require_http_methods(["POST"])
def delete_forecastModel(request):
    model_id = request.POST.get("model_id")

    delete_model_file('all', model_id)

    return JsonResponse({"status": "success"})


def train_forecastModel(request):
    model_id = request.POST.get("model_id")

    forecastModel = ForecastModel.objects.get(id=model_id)

    model_type = forecastModel.model_type
    forecastModel.model_status = "训练中...0%"
    forecastModel_data = forecastModel.model_data.split(",")[:-1]
    forecastModel.save()

    data_path_list = []

    for data_id in forecastModel_data:
        turbineData = TurbineData.objects.get(id=data_id)
        data_path = turbineData.data_path
        data_path_list.append(data_path)

    if model_type == "MLP":
        train_mlp.start_train(data_path_list, forecastModel.id)
    elif model_type == "GCN+LSTM":
        train_gcn_lstm.start_train(data_path_list, forecastModel.id)
    elif model_type == "GCN+LSTM+MLP":
        train_gcn_lstm_mlp.start_train(data_path_list, forecastModel.id)

    websiteStatistics = WebsiteStatistics.objects.first()
    websiteStatistics.statistics_train += 1

    global startTime
    currentTime = datetime.now().timestamp()
    websiteStatistics.statistics_time += currentTime - startTime

    startTime = currentTime

    websiteStatistics.save()

    return JsonResponse({"status": "success"})


@require_http_methods(["GET"])
def get_forecastTask(request):
    turbine_id = request.POST.get("turbine_id")
    task_id = request.POST.get("task_id")
    if not turbine_id:
        turbine_id = "all"
    if not task_id:
        task_id = "all"
    if turbine_id == "all" and task_id == "all":
        forecastTask = ForecastTask.objects.filter()
    elif turbine_id == "all":
        forecastTask = ForecastTask.objects.filter(id=task_id)
    elif task_id == "all":
        forecastTask = ForecastTask.objects.filter(turbine_id=turbine_id)
    else:
        forecastTask = ForecastTask.objects.filter(turbine_id=turbine_id, id=task_id)

    forecastTask_json = serializers.serialize("json", forecastTask)
    forecastTask_dict = json.loads(forecastTask_json)
    return JsonResponse(forecastTask_dict, safe=False)


@require_http_methods(["POST"])
def add_forecastTask(request):
    turbine_id = request.POST.get("turbine_id")
    task_comment = request.POST.get("task_comment")
    model_id = request.POST.get("model_id")
    data_id = request.POST.get("data_id")
    task_startTime = request.POST.get("task_startTime")
    task_endTime = request.POST.get("task_endTime")

    forcastModel = ForecastModel.objects.get(id=model_id)
    model_type = forcastModel.model_type

    turbineData = TurbineData.objects.get(id=data_id)
    data_name = turbineData.data_name

    task_status = "待预测"

    forecastTask = ForecastTask(turbine_id=turbine_id, model_id=model_id,model_type=model_type,
                                task_comment=task_comment, task_status=task_status,
                                data_name=data_name, data_id=data_id,
                                task_startTime=task_startTime, task_endTime=task_endTime)
    forecastTask.save()
    return JsonResponse({"status": "success"})


@require_http_methods(["POST"])
def delete_forecastTask(request):
    task_id = request.POST.get("task_id")
    delete_task_file('none', task_id)
    return JsonResponse({"status": "success"})


@require_http_methods(["POST"])
def start_forecastTask(request):
    task_id = request.POST.get("task_id")

    forecastTask = ForecastTask.objects.get(id=task_id)

    turbine_id = forecastTask.turbine_id
    start_time = forecastTask.task_startTime
    end_time = forecastTask.task_endTime

    forecastTask.task_status = "预测中...0%"
    forecastTask.save()

    model_id = forecastTask.model_id
    forecastModel = ForecastModel.objects.get(id=model_id)
    model_type = forecastModel.model_type
    model_path = forecastModel.model_path

    turbineData = TurbineData.objects.get(id=forecastTask.data_id)
    data_path = turbineData.data_path

    if model_type == "MLP":
        predict_mlp.start_predict(task_id, turbine_id, model_path, data_path, start_time, end_time)
    elif model_type == "GCN+LSTM":
        predict_gcn_lstm.start_predict(task_id, turbine_id, model_path, data_path, start_time, end_time)
    elif model_type == "GCN+LSTM+MLP":
        predict_mlp.start_predict(task_id, turbine_id, model_path, data_path, start_time, end_time)

    websiteStatistics = WebsiteStatistics.objects.first()
    websiteStatistics.statistics_forecast += 1

    global startTime
    currentTime = datetime.now().timestamp()
    websiteStatistics.statistics_time += currentTime - startTime

    startTime = currentTime

    websiteStatistics.save()
    return JsonResponse({"status": "success"})


@require_http_methods(["GET"])
def get_dataContent(request):
    data_id = request.GET.get("data_id")
    turbineData = TurbineData.objects.get(id=data_id)
    data_path = turbineData.data_path
    data_type = turbineData.data_type

    if data_type == "train":
        df = pd.read_csv(os.path.join(data_path),
                         parse_dates=['DATATIME'],
                         infer_datetime_format=True,
                         dayfirst=True)
    else:
        df = pd.read_csv(os.path.join(data_path),
                         parse_dates=['DATATIME'],
                         infer_datetime_format=True)

    df['DATATIME'] = pd.to_datetime(df['DATATIME'])
    df = df.sort_values(by='DATATIME', ascending=True)
    df = df.drop_duplicates(subset='DATATIME', keep='first')
    df.dropna(inplace=True)
    df = df.set_index('DATATIME')
    df = df.resample('15T').fillna(method='ffill').reset_index()
    df = df.fillna(method='ffill').reset_index()
    df = df.drop(['index'], axis=1)
    #DATATIME列转为日期字符串
    df['DATATIME'] = df['DATATIME'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    dataContent = df.to_json()

    return JsonResponse(dataContent, safe=False)


realtimeData = pd.read_csv(os.path.join('data', 'realtimeData.csv'),
                        parse_dates=['DATATIME'],
                        infer_datetime_format=True,
                        )
realtimeData['DATATIME'] = pd.to_datetime(realtimeData['DATATIME'])
realtimeData = realtimeData.sort_values(by='DATATIME', ascending=True)
realtimeData = realtimeData.drop_duplicates(subset='DATATIME', keep='first')
realtimeData.loc[realtimeData['YD15'].isnull(), 'YD15'] = realtimeData.loc[realtimeData['YD15'].isnull(), 'ROUND(A.POWER,0)']
realtimeData.dropna(inplace=True)
realtimeData = realtimeData.set_index('DATATIME')
realtimeData = realtimeData.resample('15T').fillna(method='ffill').reset_index()
realtimeData = realtimeData.fillna(method='ffill').reset_index()
realtimeData = realtimeData.drop(['index'], axis=1)
currentIndex = random.randint(0, 1000)

def get_realtimeData(location):
    global currentIndex
    currentIndex += 1
    return realtimeData.iloc[currentIndex:currentIndex+96]


@require_http_methods(["GET"])
def get_realtimePredict(request):
    turbine_id = request.GET.get("turbine_id")
    currentData = get_realtimeData(turbine_id)
    modelPath = os.path.join('model',  turbine_id, 'mlp')
    modelId = os.listdir(modelPath)[0]

    forecastModel = ForecastModel.objects.get(id=modelId)
    modelPath = forecastModel.model_path

    result = predict_mlp.realtime_predict(currentData, modelPath)

    result['DATATIME'] = result['DATATIME'].apply(lambda x: x.strftime('%H:%M:%S'))

    result = result.to_json()
    return JsonResponse(result, safe=False)


@require_http_methods(["GET"])
def get_statistics(request):
    global startTime
    currentTime = datetime.now().timestamp()
    timeIncrement = currentTime - startTime
    startTime = currentTime
    webStatistics = WebsiteStatistics.objects.first()
    webStatistics.statistics_time += timeIncrement
    webStatistics.save()

    websiteStatistics = WebsiteStatistics.objects.all()
    websiteStatistics_json = serializers.serialize("json", websiteStatistics)
    websiteStatistics_dict = json.loads(websiteStatistics_json)

    websiteStatistics = websiteStatistics[0]
    websiteStatistics.save()

    websiteStatistics = websiteStatistics_dict

    forecastModel = ForecastModel.objects.all()
    modelNum = len(forecastModel)

    turbine = Turbine.objects.all()
    turbineNum = len(turbine)

    turbineData = TurbineData.objects.all()
    dataNum = len(turbineData)

    forecastTask = ForecastTask.objects.all()
    taskNum = len(forecastTask)

    guestbook = GuestBook.objects.all()
    guestbookNum = len(guestbook)

    websiteStatistics[0]['modelNum'] = modelNum
    websiteStatistics[0]['turbineNum'] = turbineNum
    websiteStatistics[0]['dataNum'] = dataNum
    websiteStatistics[0]['taskNum'] = taskNum
    websiteStatistics[0]['guestbookNum'] = guestbookNum

    return JsonResponse(websiteStatistics, safe=False)

@require_http_methods(["GET"])
def get_guestbook(request):
    guestBook = GuestBook.objects.all()
    guestBook_json = serializers.serialize("json", guestBook)
    guestBook_dict = json.loads(guestBook_json)
    guestBook = guestBook_dict
    return JsonResponse(guestBook, safe=False)

@require_http_methods(["POST"])
def add_guestbook(request):
    guest_name = request.POST.get("guest_name")
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    guest_comment = request.POST.get("guest_comment")

    guestBook = GuestBook(guest_name=guest_name, guest_time=current_time, guest_comment=guest_comment)
    guestBook.save()
    return JsonResponse({"status": "success"})


@require_http_methods(["GET"])
def get_useAge(request):
    cpu_usage = psutil.cpu_percent(interval=1)

    result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv'], capture_output=True)
    output = result.stdout.decode('utf-8')
    gpu_usage = re.search('\d+', output).group(0)

    memory_usage = psutil.virtual_memory().percent

    disk_usage = psutil.disk_usage('/').percent

    return JsonResponse({"cpu_usage": cpu_usage, "gpu_usage": gpu_usage, "memory_usage": memory_usage, "disk_usage": disk_usage})


@require_http_methods(["POST"])
def hello_gpt(request):
    openai.api_key = "123

    messageHistory = request.POST.get("messageHistory")
    messageHistory = json.loads(messageHistory)
    messageHistory = [{'role': "system", 'content': "你是风电预测系统的AI助手，你的名字叫小风。"}] + messageHistory
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messageHistory,
    )
    print(completion)
    return JsonResponse({"message": completion.choices[0].message})

