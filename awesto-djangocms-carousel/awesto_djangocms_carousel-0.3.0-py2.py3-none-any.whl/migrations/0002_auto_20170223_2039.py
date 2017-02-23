# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_carousel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carouselpicture',
            name='image',
        ),
        migrations.RemoveField(
            model_name='carouselpicture',
            name='page',
        ),
        migrations.RemoveField(
            model_name='carouselpicture',
            name='plugin',
        ),
        migrations.AlterField(
            model_name='carouselplugin',
            name='interval',
            field=models.PositiveIntegerField(verbose_name='Interval', default=5),
        ),
        migrations.DeleteModel(
            name='CarouselPicture',
        ),
    ]
