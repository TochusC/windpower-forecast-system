from django.db import models


class Turbine(models.Model):
    turbine_id = models.CharField(max_length=20, primary_key=True)
    turbine_name = models.CharField(max_length=20)
    turbine_comment = models.CharField(max_length=80)
    turbine_status = models.CharField(max_length=20)

    def __str__(self):
        return self.turbine_id


class TurbineData(models.Model):
    id = models.AutoField(primary_key=True)
    turbine_id = models.CharField(max_length=20)
    data_name = models.CharField(max_length=20)
    data_type = models.CharField(max_length=20)
    data_size = models.CharField(max_length=20)
    data_path = models.CharField(max_length=80, unique=True)
    data_comment = models.CharField(max_length=40)
    data_uploadTime = models.CharField(max_length=40)
    data_startTime = models.CharField(max_length=40)
    data_endTime = models.CharField(max_length=40)


class ForecastModel(models.Model):
    id = models.AutoField(primary_key=True)
    turbine_id = models.CharField(max_length=20)
    model_type = models.CharField(max_length=20)
    model_data = models.CharField(max_length=60)
    model_size = models.CharField(max_length=20)
    model_path = models.CharField(max_length=80)
    model_status = models.CharField(max_length=20)
    model_comment = models.CharField(max_length=80)
    model_trainTime = models.CharField(max_length=40)


class ForecastTask(models.Model):
    id = models.AutoField(primary_key=True)
    turbine_id = models.CharField(max_length=20)
    model_id = models.CharField(max_length=20)
    model_type = models.CharField(max_length=20, default="0")
    data_id = models.CharField(max_length=20, default="0")
    data_name = models.CharField(max_length=20, default="0")
    task_status = models.CharField(max_length=20)
    task_startTime = models.CharField(max_length=40)
    task_endTime = models.CharField(max_length=40)
    task_finishTime = models.CharField(max_length=40)
    task_comment = models.CharField(max_length=80)
    result_id = models.CharField(max_length=20, default="0")


class WebsiteStatistics(models.Model):
    statistics_time = models.IntegerField(default=0)
    statistics_visit = models.IntegerField(default=0)
    statistics_download = models.IntegerField(default=0)
    statistics_upload = models.IntegerField(default=0)
    statistics_train = models.IntegerField(default=0)
    statistics_forecast = models.IntegerField(default=0)
    statistics_uploadTurbine = models.IntegerField(default=0)


class GuestBook(models.Model):
    guest_name = models.CharField(max_length=20)
    guest_comment = models.CharField(max_length=200)
    guest_time = models.CharField(max_length=40)

