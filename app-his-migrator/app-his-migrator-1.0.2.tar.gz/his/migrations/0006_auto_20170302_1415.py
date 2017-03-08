# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0005_auto_20170302_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tramahis',
            name='estado_descripcion',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='tramahis',
            name='tramaJson',
            field=models.TextField(null=True),
        ),
    ]
