# Generated by Django 2.2.10 on 2020-03-03 21:11

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("budgetportal", "0042_auto_20200131_1500"),
    ]

    operations = [
        migrations.AlterField(
            model_name="infrastructureprojectpart",
            name="gps_code",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="infrastructureprojectpart",
            name="provinces",
            field=models.CharField(default="", max_length=510),
        ),
        migrations.RenameField(
            model_name="infrastructureprojectpart",
            old_name="sphere",
            new_name="administration_type",
        ),
        migrations.RenameField(
            model_name="infrastructureprojectpart",
            old_name="department",
            new_name="government_institution",
        ),
        migrations.AddField(
            model_name="infrastructureprojectpart",
            name="date_of_close",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="infrastructureprojectpart",
            name="duration",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="infrastructureprojectpart",
            name="financing_structure",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="infrastructureprojectpart",
            name="form_of_payment",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="infrastructureprojectpart",
            name="partnership_type",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="infrastructureprojectpart",
            name="project_value_rand_million",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.RenameField(
            model_name="infrastructureprojectpart",
            old_name="amount",
            new_name="amount_rands",
        ),
        migrations.RenameField(
            model_name="infrastructureprojectpart",
            old_name="total_project_cost",
            new_name="project_value_rands",
        ),
    ]
