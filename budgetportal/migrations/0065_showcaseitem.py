# Generated by Django 2.2.28 on 2023-02-17 14:16

import budgetportal.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetportal', '0064_auto_20200728_1054'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowcaseItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=400)),
                ('button_text_1', models.CharField(max_length=200)),
                ('button_link_1', models.URLField(blank=True, null=True)),
                ('button_text_2', models.CharField(max_length=200)),
                ('button_link_2', models.URLField(blank=True, null=True)),
                ('file', models.FileField(upload_to=budgetportal.models.irm_snapshot_file_path)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]
