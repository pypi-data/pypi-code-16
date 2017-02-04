# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('yaacl', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='acl',
            name='group',
            field=models.ManyToManyField(related_name='acl', verbose_name='User', to='auth.Group', blank=True),
        ),
        migrations.AddField(
            model_name='acl',
            name='user',
            field=models.ManyToManyField(related_name='acl', verbose_name='User', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
