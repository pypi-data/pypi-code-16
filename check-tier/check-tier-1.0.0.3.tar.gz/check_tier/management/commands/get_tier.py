from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import sys

class Command(BaseCommand):
    help = 'get settings'

    def add_arguments(self, parser):
        parser.add_argument('expected_tier', type=str)


    def handle(self, *args, **options):
        tier = None
        expected_tier = options['expected_tier']
        try:
            tier = settings.TIER
        except:
            teir = 'none'
        if tier == expected_tier:
            self.stdout.write('%s' % tier)
            sys.exit(0)
        else:
            self.stdout.write("TIER SETTING INCORRECT")
            sys.exit(1)
