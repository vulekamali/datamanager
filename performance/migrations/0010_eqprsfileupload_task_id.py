# Generated by Django 2.2.28 on 2023-01-13 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("performance", "0009_auto_20230113_1028"),
    ]

    operations = [
        migrations.AddField(
            model_name="eqprsfileupload",
            name="task_id",
            field=models.TextField(default="WASN'T SET WHEN FIELD WAS ADDED"),
            preserve_default=False,
        ),
    ]
