# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('his', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TramaHis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tramaJson', models.TextField()),
                ('enviado', models.BooleanField(default=False)),
                ('fechaCreacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('fechaEnviado', models.DateTimeField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='diagnostico',
            name='labs',
        ),
        migrations.RemoveField(
            model_name='diagnostico_lab',
            name='diagnostico',
        ),
        migrations.RemoveField(
            model_name='diagnostico_lab',
            name='lab',
        ),
        migrations.RemoveField(
            model_name='trama',
            name='items',
        ),
        migrations.RemoveField(
            model_name='trama',
            name='paciente',
        ),
        migrations.RemoveField(
            model_name='trama',
            name='personal_atiende',
        ),
        migrations.RemoveField(
            model_name='trama',
            name='personal_registra',
        ),
        migrations.RemoveField(
            model_name='trama_item',
            name='item',
        ),
        migrations.RemoveField(
            model_name='trama_item',
            name='trama',
        ),
        migrations.DeleteModel(
            name='Diagnostico',
        ),
        migrations.DeleteModel(
            name='Diagnostico_Lab',
        ),
        migrations.DeleteModel(
            name='Lab',
        ),
        migrations.DeleteModel(
            name='Paciente',
        ),
        migrations.DeleteModel(
            name='Personal',
        ),
        migrations.DeleteModel(
            name='Trama',
        ),
        migrations.DeleteModel(
            name='Trama_Item',
        ),
    ]
