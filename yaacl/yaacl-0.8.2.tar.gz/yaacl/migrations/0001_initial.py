# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ACL',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True,
                )),
                ('resource', models.CharField(
                    max_length=255,
                    verbose_name='Resource name',
                    db_index=True,
                )),
                ('display', models.CharField(
                    max_length=255,
                    null=True,
                    verbose_name='displayed name',
                    blank=True,
                )),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Creation time',
                )),
                ('is_available', models.BooleanField(
                    default=True,
                    verbose_name='Is available to assign',
                )),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
