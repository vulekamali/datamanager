# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-14 10:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetportal', '0004_government-unique-together-constraints'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='department',
            name='slug',
            field=models.SlugField(max_length=200),
        ),
        migrations.AlterField(
            model_name='department',
            name='vote_number',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together=set([('government', 'slug'), ('government', 'name'), ('government', 'vote_number')]),
        ),
    ]
