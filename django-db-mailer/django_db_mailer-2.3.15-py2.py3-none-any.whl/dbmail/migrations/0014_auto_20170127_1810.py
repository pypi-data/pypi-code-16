# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dbmail', '0013_auto_20160923_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailbasetemplate',
            name='message',
            field=ckeditor.fields.RichTextField(help_text='Basic template for mail messages. {{content}} tag for msg.', verbose_name='Body'),
        ),
        migrations.AlterField(
            model_name='maillog',
            name='backend',
            field=models.CharField(default=b'mail', editable=False, choices=[(b'bot', b'dbmail.backends.bot'), (b'mail', b'dbmail.backends.mail'), (b'push', b'dbmail.backends.push'), (b'sms', b'dbmail.backends.sms'), (b'tts', b'dbmail.backends.tts')], max_length=25, verbose_name='Backend', db_index=True),
        ),
        migrations.AlterField(
            model_name='mailsubscription',
            name='backend',
            field=models.CharField(default=b'dbmail.backends.mail', max_length=50, verbose_name='Backend', choices=[(b'dbmail.backends.mail', 'MailBox'), (b'dbmail.backends.push', 'Push'), (b'dbmail.backends.sms', 'SMS'), (b'dbmail.backends.tts', 'TTS'), (b'dbmail.backends.bot', 'BOT')]),
        ),
        migrations.AlterField(
            model_name='mailtemplate',
            name='message',
            field=ckeditor.fields.RichTextField(verbose_name='Body'),
        ),
    ]
