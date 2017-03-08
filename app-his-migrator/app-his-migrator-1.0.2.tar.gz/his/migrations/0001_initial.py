# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Diagnostico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=10)),
                ('tipo_item', models.CharField(max_length=2)),
                ('tipo_diag', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Diagnostico_Lab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('diagnostico', models.ForeignKey(to='his.Diagnostico')),
            ],
        ),
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.IntegerField(null=True)),
                ('valor', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_tipo_doc', models.IntegerField()),
                ('nro_documento', models.CharField(max_length=15)),
                ('ape_paterno', models.CharField(max_length=50)),
                ('ape_materno', models.CharField(max_length=50, null=True)),
                ('nombres', models.CharField(max_length=150)),
                ('fecha_nacimiento', models.CharField(max_length=8)),
                ('id_sexo', models.CharField(max_length=1)),
                ('id_etnia', models.CharField(max_length=3)),
                ('id_ubigeo_nacimiento', models.CharField(max_length=6, null=True)),
                ('id_ubigeo_residencia', models.CharField(max_length=6, null=True)),
                ('id_ubigeo_residencia_actual', models.CharField(max_length=6, null=True)),
                ('domicilio_residencia', models.CharField(max_length=250, null=True)),
                ('domicilio_residencia_actual', models.CharField(max_length=250, null=True)),
                ('id_grado_instruccion', models.CharField(max_length=1, null=True)),
                ('id_estado_civil', models.CharField(max_length=1, null=True)),
                ('id_pais', models.CharField(max_length=1, null=True)),
                ('nro_historia_clinica', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Personal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_tipo_doc', models.IntegerField()),
                ('nro_documento', models.CharField(max_length=15)),
                ('ape_paterno', models.CharField(max_length=50)),
                ('ape_materno', models.CharField(max_length=50, null=True)),
                ('nombres', models.CharField(max_length=150)),
                ('fecha_nacimiento', models.CharField(max_length=8)),
                ('id_sexo', models.CharField(max_length=1)),
                ('id_ubigeo_nacimiento', models.CharField(max_length=6, null=True)),
                ('id_ubigeo_residencia', models.CharField(max_length=6, null=True)),
                ('id_ubigeo_residencia_actual', models.CharField(max_length=6, null=True)),
                ('domicilio_residencia', models.CharField(max_length=250, null=True)),
                ('domicilio_residencia_actual', models.CharField(max_length=250, null=True)),
                ('id_grado_instruccion', models.CharField(max_length=1, null=True)),
                ('id_estado_civil', models.CharField(max_length=1, null=True)),
                ('id_pais', models.CharField(max_length=1, null=True)),
                ('id_profesion', models.CharField(max_length=2)),
                ('id_condicion', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Trama',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_sistema', models.IntegerField()),
                ('id_financiador', models.IntegerField()),
                ('fg_sis', models.IntegerField()),
                ('componente', models.CharField(max_length=1, null=True)),
                ('fecha_atencion', models.DateTimeField()),
                ('id_turno', models.CharField(max_length=1)),
                ('id_tipcond_estab', models.CharField(max_length=1)),
                ('id_tipcond_serv', models.CharField(max_length=1)),
                ('esta_reg', models.CharField(max_length=1)),
                ('id_ups', models.CharField(max_length=6)),
                ('id_establecimiento', models.IntegerField()),
                ('edad_reg', models.IntegerField()),
                ('num_afil', models.CharField(max_length=15, null=True)),
                ('annio_edad', models.IntegerField()),
                ('mes_edad', models.IntegerField()),
                ('dia_edad', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Trama_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.ForeignKey(to='his.Diagnostico')),
                ('trama', models.ForeignKey(to='his.Trama')),
            ],
        ),
        migrations.AddField(
            model_name='trama',
            name='items',
            field=models.ManyToManyField(to='his.Diagnostico', through='his.Trama_Item'),
        ),
        migrations.AddField(
            model_name='trama',
            name='paciente',
            field=models.ForeignKey(to='his.Paciente'),
        ),
        migrations.AddField(
            model_name='trama',
            name='personal_atiende',
            field=models.ForeignKey(related_name='personal_atiende', to='his.Personal'),
        ),
        migrations.AddField(
            model_name='trama',
            name='personal_registra',
            field=models.ForeignKey(related_name='personal_registra', to='his.Personal'),
        ),
        migrations.AddField(
            model_name='diagnostico_lab',
            name='lab',
            field=models.ForeignKey(to='his.Lab'),
        ),
        migrations.AddField(
            model_name='diagnostico',
            name='labs',
            field=models.ManyToManyField(to='his.Lab', through='his.Diagnostico_Lab'),
        ),
    ]
