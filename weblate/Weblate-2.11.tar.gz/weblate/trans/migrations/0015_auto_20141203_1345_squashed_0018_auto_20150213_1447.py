# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('trans', '0015_auto_20141203_1345'), ('trans', '0016_auto_20141208_1029'), ('trans', '0017_auto_20150108_1424'), ('trans', '0018_auto_20150213_1447')]

    dependencies = [
        ('trans', '0014_auto_20141202_1101'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='source',
            options={'permissions': (('edit_priority', 'Can edit priority'), ('edit_flags', 'Can edit check flags'))},
        ),
        migrations.AlterModelOptions(
            name='subproject',
            options={'ordering': ['project__name', 'name'], 'permissions': (('lock_subproject', 'Can lock translation for translating'), ('can_see_git_repository', 'Can see VCS repository URL'))},
        ),
        migrations.AlterModelOptions(
            name='translation',
            options={'ordering': ['language__name'], 'permissions': (('upload_translation', 'Can upload translation'), ('overwrite_translation', 'Can overwrite with translation upload'), ('author_translation', 'Can define author of translation upload'), ('commit_translation', 'Can force commiting of translation'), ('update_translation', 'Can update translation from VCS'), ('push_translation', 'Can push translations to remote VCS'), ('reset_translation', 'Can reset translations to match remote VCS'), ('automatic_translation', 'Can do automatic translation'), ('lock_translation', 'Can lock whole translation project'), ('use_mt', 'Can use machine translation'))},
        ),
        migrations.AlterField(
            model_name='check',
            name='check',
            field=models.CharField(choices=[(b'end_space', 'Trailing space'), (b'begin_space', 'Starting spaces'), (b'python_brace_format', 'Python brace format'), (b'plurals', 'Missing plurals'), (b'escaped_newline', 'Mismatched \\n'), (b'end_exclamation', 'Trailing exclamation'), (b'php_format', 'PHP format'), (b'same', 'Unchanged translation'), (b'xml-tags', 'XML tags mismatch'), (b'bbcode', 'Mismatched BBcode'), (b'zero-width-space', 'Zero-width space'), (b'c_format', 'C format'), (b'end_colon', 'Trailing colon'), (b'end_question', 'Trailing question'), (b'end_ellipsis', 'Trailing ellipsis'), (b'end_stop', 'Trailing stop'), (b'begin_newline', 'Starting newline'), (b'inconsistent', 'Inconsistent'), (b'end_newline', 'Trailing newline'), (b'python_format', 'Python format')], max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='mail',
            field=models.EmailField(blank=True, help_text='Mailing list for translators.', max_length=254, verbose_name='Mailing list'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='committer_email',
            field=models.EmailField(default=b'noreply@weblate.org', max_length=254, verbose_name='Committer email'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='report_source_bugs',
            field=models.EmailField(blank=True, help_text='Email address where errors in source string will be reported, keep empty for no emails.', max_length=254, verbose_name='Source string bug report address'),
        ),
        migrations.AlterField(
            model_name='change',
            name='action',
            field=models.IntegerField(choices=[(0, 'Resource update'), (1, 'Translation completed'), (2, 'Translation changed'), (5, 'New translation'), (3, 'Comment added'), (4, 'Suggestion added'), (6, 'Automatic translation'), (7, 'Suggestion accepted'), (8, 'Translation reverted'), (9, 'Translation uploaded'), (10, 'Glossary added'), (11, 'Glossary updated'), (12, 'Glossary uploaded'), (13, 'New source string'), (14, 'Component locked'), (15, 'Component unlocked')], default=2),
        ),
    ]
