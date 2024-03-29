# Generated by Django 3.2.7 on 2021-10-20 06:47

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0016_auto_20211015_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 10, 20, 6, 47, 57, 964408, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='log',
            name='time',
            field=models.TimeField(default=datetime.datetime(2021, 10, 20, 6, 47, 57, 964439, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 20, 6, 47, 57, 965004, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='deadline',
            field=models.DateField(blank=True, default='', null=True),
        ),
    ]
