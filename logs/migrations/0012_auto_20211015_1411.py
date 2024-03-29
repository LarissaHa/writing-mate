# Generated by Django 3.2.7 on 2021-10-15 12:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0011_auto_20211007_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='deadline',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 10, 15, 12, 11, 32, 130668, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='log',
            name='time',
            field=models.TimeField(default=datetime.datetime(2021, 10, 15, 12, 11, 32, 165072, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 15, 12, 11, 32, 165630, tzinfo=utc)),
        ),
    ]
