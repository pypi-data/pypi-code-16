from __future__ import unicode_literals

import logging
from collections import OrderedDict
from shutil import rmtree

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

import boundaries
from boundaries.management.commands.loadshapefiles import create_data_sources
from boundaries.models import app_settings, Definition

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _('Reports the number of features to be loaded, along with names and identifiers.')

    def add_arguments(self, parser):
        parser.add_argument('-d', '--data-dir', action='store', dest='data_dir',
            default=app_settings.SHAPEFILES_DIR,
            help=_('Load shapefiles from this directory.'))

    def handle(self, *args, **options):
        boundaries.autodiscover(options['data_dir'])

        for slug, definition in boundaries.registry.items():
            # Backwards-compatibility with having the name, instead of the slug,
            # as the first argument to `boundaries.register`.
            definition.setdefault('name', name)
            definition = Definition(definition)

            data_sources, tmpdirs = create_data_sources(definition['file'], encoding=definition['encoding'], convert_3d_to_2d=options['clean'])

            try:
                if not data_sources:
                    log.warning(_('No shapefiles found.'))
                else:
                    features = OrderedDict()
                    for data_source in data_sources:
                        name = data_source.name
                        features[name] = []
                        layer = data_source[0]
                        for feature in layer:
                            feature = Feature(feature, definition, srs, boundary_set)
                            if feature.is_valid():
                                features[name].append([feature.id, feature.name])

                    for name, features in features.items():
                        print('%s: %d' % (name, len(features)))
                        for properties in features:
                            print('%s: %s' % properties)
            finally:
                for tmpdir in tmpdirs:
                    rmtree(tmpdir)
