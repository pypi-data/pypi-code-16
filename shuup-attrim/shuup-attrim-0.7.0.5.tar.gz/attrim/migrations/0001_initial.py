# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import attrim.types
import enumfields.fields
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            bases=(models.Model, attrim.types.TypeMixin),
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('code', models.SlugField(unique=True)),
                ('type', enumfields.fields.EnumIntegerField(enum=attrim.types.AttrimType)),
                ('product_type', models.ForeignKey(related_query_name='attrim_cls', blank=True, to='shuup.ProductType', related_name='attrim_classes', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model, attrim.types.TypeMixin),
        ),
        migrations.CreateModel(
            name='ClassTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('language_code', models.CharField(db_index=True, verbose_name='Language', max_length=15)),
                ('name', models.CharField(verbose_name='name', max_length=64)),
                ('master', models.ForeignKey(editable=False, to='attrim.Class', related_name='translations', null=True)),
            ],
            options={
                'verbose_name': 'class Translation',
                'managed': True,
                'default_permissions': (),
                'db_table': 'attrim_class_translation',
                'db_tablespace': '',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('number_value', models.DecimalField(decimal_places=9, verbose_name='numeric value', max_digits=36, blank=True, null=True)),
                ('str_value', models.TextField(blank=True)),
                ('attribute', models.ManyToManyField(related_name='option_models', blank=True, to='attrim.Attribute', related_query_name='option_model')),
                ('cls', models.ForeignKey(related_query_name='option_model', blank=True, to='attrim.Class', related_name='option_models', null=True)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OptionTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('language_code', models.CharField(db_index=True, verbose_name='Language', max_length=15)),
                ('trans_str_value', models.TextField(blank=True)),
                ('master', models.ForeignKey(editable=False, to='attrim.Option', related_name='translations', null=True)),
            ],
            options={
                'verbose_name': 'option Translation',
                'managed': True,
                'default_permissions': (),
                'db_table': 'attrim_option_translation',
                'db_tablespace': '',
            },
        ),
        migrations.AddField(
            model_name='attribute',
            name='cls',
            field=models.ForeignKey(related_name='attrim', to='attrim.Class'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='product',
            field=models.ForeignKey(related_query_name='attrim', to='shuup.Product', related_name='attrims'),
        ),
        migrations.AlterUniqueTogether(
            name='optiontranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='classtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together=set([('product', 'cls')]),
        ),
    ]
