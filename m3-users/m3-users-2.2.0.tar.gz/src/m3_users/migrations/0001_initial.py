# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-01-10 16:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'm3_users_assignedrole',
                'verbose_name': 'Связка роли с пользователем',
                'verbose_name_plural': 'Связки ролей с пользователями',
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_code', models.CharField(db_index=True, max_length=200, verbose_name='Код права доступа')),
                ('verbose_permission_name', models.TextField(verbose_name='Описание права доступа')),
                ('disabled', models.BooleanField(default=False, verbose_name='Активно')),
            ],
            options={
                'db_table': 'm3_users_rolepermissions',
                'verbose_name': 'Право доступа у роли',
                'verbose_name_plural': 'Права доступа у ролей',
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, verbose_name='Наименование роли пользователя')),
                ('metarole', models.CharField(blank=True, max_length=100, null=True, verbose_name='Метароль')),
            ],
            options={
                'db_table': 'm3_users_role',
                'verbose_name': 'Роль пользователя',
                'verbose_name_plural': 'Роли пользователя',
            },
        ),
        migrations.AddField(
            model_name='rolepermission',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='m3_users.UserRole', verbose_name='Роль'),
        ),
        migrations.AddField(
            model_name='assignedrole',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_users', to='m3_users.UserRole', verbose_name='Роль'),
        ),
    ]
