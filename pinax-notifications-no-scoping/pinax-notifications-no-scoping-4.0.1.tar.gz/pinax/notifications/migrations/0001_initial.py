# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeQueueBatch',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('pickled_data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='NoticeSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('medium', models.CharField(verbose_name='medium', choices=[(0, 'email')], max_length=1)),
                ('send', models.BooleanField(verbose_name='send', default=False)),
            ],
            options={
                'verbose_name': 'notice setting',
                'verbose_name_plural': 'notice settings',
            },
        ),
        migrations.CreateModel(
            name='NoticeType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(verbose_name='label', max_length=40)),
                ('display', models.CharField(verbose_name='display', max_length=50)),
                ('description', models.CharField(verbose_name='description', max_length=100)),
                ('default', models.IntegerField(verbose_name='default')),
            ],
            options={
                'verbose_name': 'notice type',
                'verbose_name_plural': 'notice types',
            },
        ),
        migrations.AddField(
            model_name='noticesetting',
            name='notice_type',
            field=models.ForeignKey(verbose_name='notice type', to='pinax_notifications.NoticeType'),
        ),
        migrations.AddField(
            model_name='noticesetting',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='noticesetting',
            unique_together=set([('user', 'notice_type', 'medium')]),
        ),
    ]
