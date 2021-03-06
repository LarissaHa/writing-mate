# Generated by Django 3.1.2 on 2020-10-26 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='tags',
        ),
        migrations.AddField(
            model_name='project',
            name='topic',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='project',
            name='goal',
            field=models.IntegerField(default=50000),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('PR', 'prepping'), ('IP', 'in progress'), ('DR', 'drafted'), ('CP', 'completed'), ('PB', 'published')], default='PR', max_length=2),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.CharField(choices=[('NO', 'novel'), ('SS', 'short story'), ('ME', 'memoir'), ('SC', 'script'), ('NF', 'nonfiction'), ('PO', 'poetry'), ('OT', 'other')], default='NO', max_length=2),
        ),
        migrations.AlterField(
            model_name='project',
            name='unit',
            field=models.CharField(choices=[('W', 'words'), ('C', 'characters'), ('M', 'minutes'), ('H', 'hours'), ('O', 'other')], default='W', max_length=1),
        ),
    ]
