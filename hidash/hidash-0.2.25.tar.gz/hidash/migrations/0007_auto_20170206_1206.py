# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import hidash.models


class Migration(migrations.Migration):

    dependencies = [
        ('hidash', '0006_auto_20161213_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='template',
            field=models.FileField(null=True, upload_to=hidash.models.get_storage_path, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledreport',
            name='email_message',
            field=models.TextField(default=b'', max_length=10000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='chart',
            name='description',
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='chart',
            name='dimension',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='chart',
            name='height',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='chart',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='scheduledreport',
            name='template',
            field=models.FileField(null=True, upload_to=hidash.models.get_storage_path, blank=True),
        ),
    ]
