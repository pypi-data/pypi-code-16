# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-26 19:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pootle_statistics', '0006_set_submission_base_manager_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='revision',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
    ]
