# Generated by Django 3.0.3 on 2022-03-06 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0005_auto_20220306_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]