# Generated by Django 2.2.20 on 2022-12-05 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("performance", "0003_remove_eqprsfileupload_file_validation_report"),
    ]

    operations = [
        migrations.AddField(
            model_name="eqprsfileupload",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="eqprsfileupload",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
