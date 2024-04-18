from django.urls import path

from WPF.views import *


urlpatterns = [
    path("add_turbine/", add_turbine),
    path("get_turbine/", get_turbine),
    path("delete_turbine/", delete_turbine),
    path("get_turbineData/", get_turbineData),
    path("upload_data/", upload_data),
    path("delete_data/", delete_data),
    path("download_data/", download_data),
    path("get_forecastModel/", get_forecastModel),
    path("add_forecastModel/", add_forecastModel),
    path('alter_forecastModel/', alter_forecastModel),
    path("train_forecastModel/", train_forecastModel),
    path("delete_forecastModel/", delete_forecastModel),
    path("get_forecastTask/", get_forecastTask),  # GET方法 用于获取预测任务列表，可选传入参数为turbine_id, task_id
    path("delete_forecastTask/", delete_forecastTask),  # POST方法 用于删除预测任务，传入参数为task_id
    path("add_forecastTask/", add_forecastTask),  # POST方法 用于添加预测任务，表单传入参数为turbine_id, model_id, task_comment, data_id(
    path("start_forecastTask/", start_forecastTask),  # POST方法 用于开始预测任务，传入参数为task_id
    path("get_dataContent/", get_dataContent),  # GET方法 用于获取数据内容，传入参数为data_id
    path("get_realtimePredict/", get_realtimePredict),  # GET方法 用于获取实时预测，传入参数为turbine_id1
    path('get_statistics/', get_statistics),  # GET方法 用于获取网站统计信息
    path('add_guestbook/', add_guestbook),  # POST方法 用于添加留言，表单传入参数为guestbook_content
    path('get_guestbook/', get_guestbook),  # GET方法 用于获取留言，可选传入参数为guestbook_id
    path('get_useAge/', get_useAge),  # GET方法
    path('hello_gpt/', hello_gpt),
]