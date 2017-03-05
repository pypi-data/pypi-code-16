# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    MiscType = apps.get_model('joda_misc', 'MiscType')
    MiscType.objects.using(db_alias).create(name='Miscellaneous')


def reverse_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    MiscType = apps.get_model('joda_misc', 'MiscType')
    MiscType.objects.using(db_alias).filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('joda_misc', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
        migrations.AlterField(
            model_name='miscdocument',
            name='misc_type',
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to='joda_misc.MiscType'),
        ),
    ]
