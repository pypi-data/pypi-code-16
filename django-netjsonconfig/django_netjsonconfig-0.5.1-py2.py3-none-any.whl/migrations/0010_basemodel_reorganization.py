# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-09 14:52
from __future__ import unicode_literals

import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_netjsonconfig', '0009_openvpn_data_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='template',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='vpn',
            name='config',
            field=jsonfield.fields.JSONField(default=dict, help_text='configuration in NetJSON DeviceConfiguration format', verbose_name='configuration'),
        ),
    ]
