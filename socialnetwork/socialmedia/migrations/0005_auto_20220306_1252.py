# Generated by Django 3.0.3 on 2022-03-06 11:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0004_auto_20220305_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='birthDate',
            field=models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='images'),
        ),
    ]
