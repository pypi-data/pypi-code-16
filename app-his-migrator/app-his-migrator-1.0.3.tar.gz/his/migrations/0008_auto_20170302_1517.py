# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0007_auto_20170302_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tramahis',
            name='fechaCreacion',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
