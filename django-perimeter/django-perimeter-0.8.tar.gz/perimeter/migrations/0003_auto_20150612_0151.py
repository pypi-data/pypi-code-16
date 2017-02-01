# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perimeter', '0002_auto_20150611_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesstokenuse',
            name='user_email',
            field=models.EmailField(max_length=254, verbose_name=b'Token used by (email)'),
        ),
    ]
