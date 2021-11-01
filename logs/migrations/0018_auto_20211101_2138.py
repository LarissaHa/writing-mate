# Generated by Django 3.2.7 on 2021-11-01 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0017_auto_20211020_0847'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='images'),
        ),
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=''),
        ),
        migrations.AlterField(
            model_name='log',
            name='time',
            field=models.TimeField(default=''),
        ),
        migrations.AlterField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(default=''),
        ),
    ]