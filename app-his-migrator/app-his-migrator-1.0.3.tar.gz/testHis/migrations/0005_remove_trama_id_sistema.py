# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testHis', '0004_trama_id_tipedad_reg'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trama',
            name='id_sistema',
        ),
    ]
