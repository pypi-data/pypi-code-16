# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0009_auto_20170302_1520'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tramahis',
            old_name='tramaJson',
            new_name='trama_cita_json',
        ),
        migrations.AddField(
            model_name='tramahis',
            name='nro_intentos',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tramahis',
            name='trama_paciente_json',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='tramahis',
            name='trama_personal_atiende',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='tramahis',
            name='trama_personal_registra',
            field=models.TextField(null=True),
        ),
    ]
