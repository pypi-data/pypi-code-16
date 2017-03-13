# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

from pixelpin_auth_core.utils import setting_name

USER_MODEL = getattr(settings, setting_name('USER_MODEL'), None) or \
             getattr(settings, 'AUTH_USER_MODEL', None) or \
             'auth.User'


class Migration(migrations.Migration):
    replaces = [
        ('default', '0002_add_related_name'),
        ('pixelpin_auth', '0002_add_related_name')
    ]

    dependencies = [
        ('pixelpin_auth_django', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpixelpinAuth',
            name='user',
            field=models.ForeignKey(related_name='pixelpin_auth', to=USER_MODEL)
        ),
    ]
