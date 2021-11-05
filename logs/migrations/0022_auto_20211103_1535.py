# Generated by Django 3.2.7 on 2021-11-03 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0021_project_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='about_me',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='color',
            field=models.CharField(blank=True, default='#5a5c69', max_length=7, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='daily_goal',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='goal_unit',
            field=models.CharField(blank=True, choices=[('words', 'words'), ('characters', 'characters'), ('pages', 'pages'), ('minutes', 'minutes'), ('hours', 'hours'), ('other', 'other')], default='words', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='header_image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='images'),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='images'),
        ),
        migrations.AddField(
            model_name='project',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]