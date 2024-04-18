# Generated by Django 4.2.1 on 2023-07-18 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("WPF", "0005_forecasttask_model_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="GuestBook",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guest_name", models.CharField(max_length=20)),
                ("guest_comment", models.CharField(max_length=200)),
                ("guest_time", models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name="WebsiteStatistics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("statistics_time", models.IntegerField(default=0)),
                ("statistics_visit", models.IntegerField(default=0)),
                ("statistics_download", models.IntegerField(default=0)),
                ("statistics_upload", models.IntegerField(default=0)),
                ("statistics_train", models.IntegerField(default=0)),
                ("statistics_forecast", models.IntegerField(default=0)),
                ("statistics_uploadTurbine", models.IntegerField(default=0)),
            ],
        ),
    ]
