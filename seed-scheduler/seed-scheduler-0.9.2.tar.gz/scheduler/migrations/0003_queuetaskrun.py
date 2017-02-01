# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-13 11:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery', '0001_initial'),
        ('scheduler', '0002_auto_20161012_2010'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueueTaskRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.UUIDField()),
                ('started_at', models.DateTimeField()),
                ('completed_at', models.DateTimeField(null=True)),
                ('celery_cron_definition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='djcelery.CrontabSchedule')),
                ('celery_interval_definition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='djcelery.IntervalSchedule')),
            ],
        ),
    ]
