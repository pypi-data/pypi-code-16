from optparse import make_option
import os
import subprocess
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
	help = 'Run schemamigration --auto for all apps under south.'

	def handle(self, *args, **options):
		for module in settings.SOUTH_MIGRATION_MODULES:
			print 'Migrating %s' % module
			result = subprocess.call([sys.argv[0], 'schemamigration', module, '--auto'])
