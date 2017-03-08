# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0006_auto_20170302_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tramahis',
            name='id_cita_his',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tramahis',
            name='id_model_base',
            field=models.IntegerField(default=0),
        ),
    ]
