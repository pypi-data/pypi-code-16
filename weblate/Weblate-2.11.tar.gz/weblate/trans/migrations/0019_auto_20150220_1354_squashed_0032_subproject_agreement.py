# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 17:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def fill_in_subproject(apps, schema_editor):
    Change = apps.get_model('trans', 'Change')

    actions = set((14, 15, 16, 18, 19, 20, 21, 22, 23))

    for change in Change.objects.all():
        if change.subproject:
            continue
        if change.action in actions and change.translation:
            change.subproject = change.translation.subproject
            change.translation = None
            change.save()
        elif change.translation:
            change.subproject = change.translation.subproject
            change.save()


class Migration(migrations.Migration):

    replaces = [('trans', '0019_auto_20150220_1354'), ('trans', '0020_auto_20150220_1356'), ('trans', '0021_auto_20150306_1605'), ('trans', '0022_auto_20150309_0932'), ('trans', '0023_project_owner'), ('trans', '0024_subproject_edit_template'), ('trans', '0025_subproject_post_update_script'), ('trans', '0026_auto_20150401_1029'), ('trans', '0027_auto_20150401_1030'), ('trans', '0028_auto_20150402_1430'), ('trans', '0029_auto_20150415_1318'), ('trans', '0030_change_subproject'), ('trans', '0031_auto_20150415_1339'), ('trans', '0032_subproject_agreement')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trans', '0018_auto_20150213_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subproject',
            name='vcs',
            field=models.CharField(choices=[(b'git', b'Git'), (b'gerrit', b'Gerrit'), (b'mercurial', b'Mercurial')], default=b'git', help_text='Version control system to use to access your repository with translations.', max_length=20, verbose_name='Version control system'),
        ),
        migrations.AlterField(
            model_name='indexupdate',
            name='unit',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='trans.Unit'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='branch',
            field=models.CharField(blank=True, default=b'', help_text='Repository branch to translate', max_length=50, verbose_name='Repository branch'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='file_format',
            field=models.CharField(choices=[(b'aresource', 'Android String Resource'), (b'auto', 'Automatic detection'), (b'json', 'JSON file'), (b'php', 'PHP strings'), (b'po', 'Gettext PO file'), (b'po-mono', 'Gettext PO file (monolingual)'), (b'properties', 'Java Properties'), (b'properties-utf8', 'Java Properties (UTF-8)'), (b'resx', '.Net resource file'), (b'strings', 'OS X Strings'), (b'strings-utf8', 'OS X Strings (UTF-8)'), (b'ts', 'Qt Linguist Translation File'), (b'xliff', 'XLIFF Translation File')], default=b'auto', help_text='Automatic detection might fail for some formats and is slightly slower.', max_length=50, verbose_name='File format'),
        ),
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(blank=True, help_text='Owner of the project.', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subproject',
            name='edit_template',
            field=models.BooleanField(default=True, help_text='Whether users will be able to edit base file for monolingual translations.', verbose_name='Edit base file'),
        ),
        migrations.AddField(
            model_name='subproject',
            name='post_update_script',
            field=models.CharField(blank=True, choices=[(b'', b'')], default=b'', help_text='Script to be executed after receiving a repository update, please check documentation for more details.', max_length=200, verbose_name='Post-update script'),
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'ordering': ['priority', 'position'], 'permissions': (('save_translation', 'Can save translation'), ('save_template', 'Can save template'))},
        ),
        migrations.AlterField(
            model_name='change',
            name='action',
            field=models.IntegerField(choices=[(0, 'Resource update'), (1, 'Translation completed'), (2, 'Translation changed'), (5, 'New translation'), (3, 'Comment added'), (4, 'Suggestion added'), (6, 'Automatic translation'), (7, 'Suggestion accepted'), (8, 'Translation reverted'), (9, 'Translation uploaded'), (10, 'Glossary added'), (11, 'Glossary updated'), (12, 'Glossary uploaded'), (13, 'New source string'), (14, 'Component locked'), (15, 'Component unlocked'), (16, 'Detected duplicate string'), (17, 'Commited changes'), (18, 'Pushed changes'), (19, 'Reset repository')], default=2),
        ),
        migrations.AlterField(
            model_name='change',
            name='action',
            field=models.IntegerField(choices=[(0, 'Resource update'), (1, 'Translation completed'), (2, 'Translation changed'), (5, 'New translation'), (3, 'Comment added'), (4, 'Suggestion added'), (6, 'Automatic translation'), (7, 'Suggestion accepted'), (8, 'Translation reverted'), (9, 'Translation uploaded'), (10, 'Glossary added'), (11, 'Glossary updated'), (12, 'Glossary uploaded'), (13, 'New source string'), (14, 'Component locked'), (15, 'Component unlocked'), (16, 'Detected duplicate string'), (17, 'Commited changes'), (18, 'Pushed changes'), (19, 'Reset repository'), (20, 'Merged repository'), (21, 'Rebased repository'), (22, 'Failed merge on repository'), (23, 'Failed rebase on repository')], default=2),
        ),
        migrations.AddField(
            model_name='change',
            name='subproject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='trans.SubProject'),
        ),
        migrations.RunPython(fill_in_subproject),
        migrations.AddField(
            model_name='subproject',
            name='agreement',
            field=models.TextField(blank=True, default=b'', help_text='Agreement which needs to be approved before user can translate this component.', verbose_name='Contributor agreement'),
        ),
    ]
