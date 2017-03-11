# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testHis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trama',
            name='annio_edad',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='dia_edad',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='edad_reg',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='esta_reg',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='fg_sis',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='id_establecimiento',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='id_financiador',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='id_sistema',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='id_tipcond_estab',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='id_tipcond_serv',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='id_turno',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='id_ups',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='items',
            field=models.ManyToManyField(to='testHis.Diagnostico', null=True, through='testHis.Trama_Item'),
        ),
        migrations.AlterField(
            model_name='trama',
            name='mes_edad',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='paciente',
            field=models.ForeignKey(to='testHis.Paciente', null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='personal_atiende',
            field=models.ForeignKey(related_name='personal_atiende', to='testHis.Personal', null=True),
        ),
        migrations.AlterField(
            model_name='trama',
            name='personal_registra',
            field=models.ForeignKey(related_name='personal_registra', to='testHis.Personal', null=True),
        ),
    ]
