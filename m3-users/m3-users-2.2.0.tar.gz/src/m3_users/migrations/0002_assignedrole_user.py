# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-01-10 16:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('m3_users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignedrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_roles', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
