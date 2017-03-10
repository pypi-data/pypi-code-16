from django.core.management.base import BaseCommand
from django.conf import settings
from ..transpiler import transpile_js

import os


class Command(BaseCommand):
    help = 'Transpiles python files to js according to the settings'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--debug',
            dest='debug',
            action='store_true',
            help='Use debug transpiler options',
        )

    def handle(self, *args, **options):
        if hasattr(settings, "TRANSCRYPT_MAINS"):

            for conf in settings.TRANSCRYPT_MAINS:
                path = conf["SRC_FILE"]
                sink_dir = conf["SINK_DIR"]
                fullpath = os.path.abspath(
                    os.path.join(path, "../"))
                main_file = os.path.basename(path)

                transpile_js(fullpath, main_file, sink_dir)()
