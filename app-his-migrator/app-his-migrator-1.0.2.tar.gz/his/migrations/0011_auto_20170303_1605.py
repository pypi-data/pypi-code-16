# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0010_auto_20170303_1521'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tramahis',
            old_name='trama_personal_atiende',
            new_name='trama_personal_atiende_json',
        ),
        migrations.RenameField(
            model_name='tramahis',
            old_name='trama_personal_registra',
            new_name='trama_personal_registra_json',
        ),
    ]
