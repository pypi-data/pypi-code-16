# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testHis', '0003_auto_20170222_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='trama',
            name='id_tipedad_reg',
            field=models.IntegerField(null=True),
        ),
    ]
