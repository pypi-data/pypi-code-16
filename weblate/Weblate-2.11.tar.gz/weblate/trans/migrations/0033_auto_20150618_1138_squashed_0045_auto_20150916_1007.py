# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 17:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import weblate.trans.fields
import weblate.trans.validators


def fill_in_owners(apps, schema_editor):
    Project = apps.get_model('trans', 'Project')

    for project in Project.objects.all():
        if project.owner:
            project.owners.add(project.owner)


def fill_in_owner(apps, schema_editor):
    Project = apps.get_model('trans', 'Project')

    for project in Project.objects.all():
        if project.owners.exists():
            project.owner = project.owners.all()[0]
            project.save()


class Migration(migrations.Migration):

    replaces = [('trans', '0033_auto_20150618_1138'), ('trans', '0034_auto_20150618_1140'), ('trans', '0035_auto_20150630_1208'), ('trans', '0036_auto_20150709_1005'), ('trans', '0037_auto_20150810_1348'), ('trans', '0038_auto_20150810_1354'), ('trans', '0039_remove_project_owner'), ('trans', '0040_auto_20150818_1643'), ('trans', '0041_auto_20150819_1457'), ('trans', '0042_auto_20150910_0854'), ('trans', '0043_auto_20150910_0909'), ('trans', '0044_auto_20150916_0952'), ('trans', '0045_auto_20150916_1007')]

    dependencies = [
        ('trans', '0032_subproject_agreement'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advertisement',
            options={'verbose_name': 'Advertisement', 'verbose_name_plural': 'Advertisements'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['name'], 'permissions': (('manage_acl', 'Can manage ACL rules for a project'),), 'verbose_name': 'Project', 'verbose_name_plural': 'Projects'},
        ),
        migrations.AlterModelOptions(
            name='subproject',
            options={'ordering': ['project__name', 'name'], 'permissions': (('lock_subproject', 'Can lock translation for translating'), ('can_see_git_repository', 'Can see VCS repository URL')), 'verbose_name': 'Component', 'verbose_name_plural': 'Components'},
        ),
        migrations.AlterModelOptions(
            name='whiteboardmessage',
            options={'verbose_name': 'Whiteboard message', 'verbose_name_plural': 'Whiteboard messages'},
        ),
        migrations.AlterField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(blank=True, help_text='Owner of the project.', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='new_lang',
            field=models.CharField(choices=[(b'contact', 'Use contact form'), (b'url', 'Point to translation instructions URL'), (b'add', 'Automatically add language file'), (b'none', 'No adding of language')], default=b'contact', help_text='How to handle requests for creating new languages. Please note that availability of choices depends on the file format.', max_length=10, verbose_name='New language'),
        ),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.SlugField(help_text='Name used in URLs and file names.', max_length=100, unique=True, verbose_name='URL slug'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='slug',
            field=models.SlugField(help_text='Name used in URLs and file names.', max_length=100, verbose_name='URL slug'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='allow_translation_propagation',
            field=models.BooleanField(db_index=True, default=True, help_text='Whether translation updates in other components will cause automatic translation in this one', verbose_name='Allow translation propagation'),
        ),
        migrations.AddField(
            model_name='subproject',
            name='post_commit_script',
            field=models.CharField(blank=True, choices=[(b'', b'')], default=b'', help_text='Script to be executed after committing translation, please check documentation for more details.', max_length=200, verbose_name='Post-commit script'),
        ),
        migrations.AddField(
            model_name='subproject',
            name='post_push_script',
            field=models.CharField(blank=True, choices=[(b'', b'')], default=b'', help_text='Script to be executed after pushing translation to remote, please check documentation for more details.', max_length=200, verbose_name='Post-push script'),
        ),
        migrations.AddField(
            model_name='project',
            name='owners',
            field=models.ManyToManyField(blank=True, help_text='Owners of the project.', to=settings.AUTH_USER_MODEL, verbose_name='Owners'),
        ),
        migrations.AlterField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(blank=True, help_text='Owner of the project.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='old_owned_projects', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.RunPython(
            fill_in_owners,
            reverse_code=fill_in_owner,
        ),
        migrations.RemoveField(
            model_name='project',
            name='owner',
        ),
        migrations.AddField(
            model_name='subproject',
            name='language_regex',
            field=weblate.trans.fields.RegexField(default=b'^[^.]+$', help_text='Regular expression which is used to filter translation when scanning for file mask.', max_length=200, verbose_name='Language filter'),
        ),
        migrations.AlterField(
            model_name='check',
            name='check',
            field=models.CharField(choices=[(b'end_space', 'Trailing space'), (b'begin_space', 'Starting spaces'), (b'bbcode', 'Mismatched BBcode'), (b'python_brace_format', 'Python brace format'), (b'plurals', 'Missing plurals'), (b'escaped_newline', 'Mismatched \\n'), (b'end_exclamation', 'Trailing exclamation'), (b'php_format', 'PHP format'), (b'same', 'Unchanged translation'), (b'xml-tags', 'XML tags mismatch'), (b'inconsistent', 'Inconsistent'), (b'zero-width-space', 'Zero-width space'), (b'c_format', 'C format'), (b'end_colon', 'Trailing colon'), (b'end_question', 'Trailing question'), (b'end_ellipsis', 'Trailing ellipsis'), (b'end_stop', 'Trailing stop'), (b'begin_newline', 'Starting newline'), (b'javascript_format', 'Javascript format'), (b'end_newline', 'Trailing newline'), (b'python_format', 'Python format')], max_length=20),
        ),
        migrations.AddField(
            model_name='subproject',
            name='post_add_script',
            field=models.CharField(blank=True, choices=[(b'', b'')], default=b'', help_text='Script to be executed after adding new translation, please check documentation for more details.', max_length=200, verbose_name='Post-add script'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='extra_commit_file',
            field=models.TextField(blank=True, default=b'', help_text='Additional files to include in commits, one per line; please check documentation for more details.', validators=[weblate.trans.validators.validate_extra_file], verbose_name='Additional commit files'),
        ),
        migrations.AlterField(
            model_name='subproject',
            name='file_format',
            field=models.CharField(choices=[(b'aresource', 'Android String Resource'), (b'auto', 'Automatic detection'), (b'csv', 'CSV file'), (b'json', 'JSON file'), (b'php', 'PHP strings'), (b'po', 'Gettext PO file'), (b'po-mono', 'Gettext PO file (monolingual)'), (b'properties', 'Java Properties'), (b'properties-utf8', 'Java Properties (UTF-8)'), (b'resx', '.Net resource file'), (b'strings', 'OS X Strings'), (b'strings-utf8', 'OS X Strings (UTF-8)'), (b'ts', 'Qt Linguist Translation File'), (b'xliff', 'XLIFF Translation File')], default=b'auto', help_text='Automatic detection might fail for some formats and is slightly slower.', max_length=50, verbose_name='File format'),
        ),
        migrations.AlterModelOptions(
            name='change',
            options={'ordering': ['-timestamp'], 'permissions': (('download_changes', 'Can download changes'),)},
        ),
    ]
