# Generated by Django 2.2.28 on 2023-02-22 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetportal', '0068_auto_20230220_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcaseitem',
            name='cta_enabled_2',
            field=models.BooleanField(default=True, verbose_name='Enable call to action 2'),
            preserve_default=False,
        ),
    ]