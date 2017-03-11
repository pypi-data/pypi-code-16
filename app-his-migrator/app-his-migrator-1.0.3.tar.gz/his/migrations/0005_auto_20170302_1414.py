# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0004_hisrest'),
    ]

    operations = [
        migrations.AddField(
            model_name='tramahis',
            name='estado_descripcion',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tramahis',
            name='estado_enviado',
            field=models.CharField(default=False, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tramahis',
            name='id_cita_his',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tramahis',
            name='id_model_base',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
