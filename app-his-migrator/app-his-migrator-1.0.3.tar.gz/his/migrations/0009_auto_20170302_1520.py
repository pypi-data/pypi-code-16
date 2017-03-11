# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0008_auto_20170302_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tramahis',
            name='fechaEnviado',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
