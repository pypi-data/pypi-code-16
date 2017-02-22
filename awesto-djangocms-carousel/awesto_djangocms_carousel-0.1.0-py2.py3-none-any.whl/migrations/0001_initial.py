# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0007_auto_20161016_1055'),
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarouselPicture',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('alt_tag', models.CharField(blank=True, max_length=255, verbose_name='Alt tag')),
                ('text', models.TextField(blank=True, verbose_name='Text over image')),
                ('url', models.CharField(blank=True, null=True, max_length=500, verbose_name='URL')),
                ('open_in_tab', models.BooleanField(verbose_name='Open in new window')),
                ('ordering', models.PositiveIntegerField(editable=False, db_index=True, default=0)),
                ('image', filer.fields.image.FilerImageField(related_name='+', verbose_name='Image', to='filer.Image')),
                ('page', cms.models.fields.PageField(verbose_name='Page', to='cms.Page', blank=True, null=True)),
            ],
            options={
                'ordering': ['ordering'],
            },
        ),
        migrations.CreateModel(
            name='CarouselPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='cms.CMSPlugin', related_name='cmsplugin_carousel_carouselplugin', serialize=False)),
                ('interval', models.PositiveIntegerField(default=1, verbose_name='Interval')),
                ('title', models.CharField(blank=True, max_length=255, default='', verbose_name='Title')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AddField(
            model_name='carouselpicture',
            name='plugin',
            field=models.ForeignKey(related_name='pictures', to='cmsplugin_carousel.CarouselPlugin'),
        ),
    ]
