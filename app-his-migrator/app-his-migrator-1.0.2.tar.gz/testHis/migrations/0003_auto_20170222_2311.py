# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testHis', '0002_auto_20170222_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trama',
            name='fecha_atencion',
            field=models.DateTimeField(null=True),
        ),
    ]
