# Generated by Django 2.2.20 on 2022-11-30 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("performance", "0003_remove_eqprsfileupload_file_validation_report"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eqprsfileupload",
            name="task",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_q.Task",
            ),
        ),
    ]
