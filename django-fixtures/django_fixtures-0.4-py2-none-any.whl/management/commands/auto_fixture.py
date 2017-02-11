# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import management
from os.path import dirname, exists
import os
import re

re_pattern = re.compile(r'([\d]+)_[\w]+\.py$')

T = '''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core import management
from fixtures.util import load_fixtures


def load(apps, schema_editor):
    load_fixtures(apps, schema_editor, '%(fixture_name)s')


class Migration(migrations.Migration):

    dependencies = [
        ('%(app)s', '%(file)s'),
    ]

    operations = [
        migrations.RunPython(load),
    ]
'''


def find_last_migration_file(app):
    for path in sorted(os.listdir('%s/migrations' % app), reverse=True):
        if re_pattern.match(path) and "load_fixtures" not in path:
            _id = re_pattern.findall(path)[0]
            return _id, '%s/migrations/%s' % (app, path)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', type=str)

    def handle(self, *args, **options):
        app = options['app']

        app_path = '%s' % app
        _id, migration_file = find_last_migration_file(app)

        fixture_name = "%s_%s" % (_id.zfill(4), app)
        path = '%s/fixtures/%s.json' % (app_path, fixture_name)
        if not exists(dirname(path)):
            os.makedirs(dirname(path))

        with open(path, 'w') as f:
            management.call_command('dumpdata', app, '-a', stdout=f)

        os.system('gzip %s' % path)

        with open('%s/migrations/%s_load_fixtures.py' % (app, str(_id).zfill(4)), 'w') as ofile:
            ofile.write(T % {
                'app': app,
                'file': os.path.basename(migration_file).split('.')[0],
                "fixture_name": fixture_name
            })
