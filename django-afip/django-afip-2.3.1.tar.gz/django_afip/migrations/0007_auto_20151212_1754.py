# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-12 17:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('afip', '0006_auto_20151212_1431'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taxpayerprofile',
            options={'verbose_name': 'taxpayer profile', 'verbose_name_plural': 'taxpayer profiles'},
        ),
        migrations.RemoveField(
            model_name='taxpayer',
            name='active_since',
        ),
        migrations.AddField(
            model_name='taxpayerprofile',
            name='active_since',
            field=models.DateField(default=None, help_text='Date since which this taxpayer has been legally active.', verbose_name='active since'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taxpayerprofile',
            name='issuing_email',
            field=models.TextField(blank=True, null=True, verbose_name='issuing email'),
        ),
        migrations.AddField(
            model_name='taxpayerprofile',
            name='sales_terms',
            field=models.CharField(default=None, help_text='The terms of the sale printed onto receipts by default (eg: single payment, checking account, etc).', max_length=48, verbose_name='sales terms'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pointofsales',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points_of_sales', to='afip.TaxPayer', verbose_name='owner'),
        ),
        migrations.AlterField(
            model_name='receiptpdf',
            name='client_name',
            field=models.CharField(max_length=128, verbose_name='client name'),
        ),
        migrations.AlterField(
            model_name='receiptpdf',
            name='issuing_email',
            field=models.CharField(max_length=128, null=True, verbose_name='issuing email'),
        ),
        migrations.AlterField(
            model_name='receiptpdf',
            name='issuing_name',
            field=models.CharField(max_length=128, verbose_name='issuing name'),
        ),
        migrations.AlterField(
            model_name='receiptpdf',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='pdf file'),
        ),
    ]
