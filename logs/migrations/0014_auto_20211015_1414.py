# Generated by Django 3.2.7 on 2021-10-15 12:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0013_auto_20211015_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 10, 15, 12, 14, 43, 691629, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='log',
            name='time',
            field=models.TimeField(default=datetime.datetime(2021, 10, 15, 12, 14, 43, 726184, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 15, 12, 14, 43, 726739, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='deadline',
            field=models.DateField(blank=True, default=datetime.datetime(2021, 10, 15, 12, 14, 43, 726792, tzinfo=utc), null=True),
        ),
    ]