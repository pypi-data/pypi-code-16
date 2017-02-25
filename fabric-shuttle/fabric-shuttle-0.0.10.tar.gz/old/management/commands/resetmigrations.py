import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
	help = 'Reset all migrations to just initial files. Also consider using the --update when doing schemamigrations.'

	def handle(self, *args, **options):
		if not hasattr(settings, 'DEBUG') or not settings.DEBUG:
			print 'This command is only valid for development, DEBUG is not True.'
			return
		for module in settings.SOUTH_MIGRATION_MODULES:
			os.system('rm -rf %s' % settings.SOUTH_MIGRATION_MODULES[module].replace('.', '/'))
			call_command('schemamigration', module, initial=True)
			if hasattr(settings, 'SOUTH_MIGRATION_DEPENDENCIES'):
				if settings.SOUTH_MIGRATION_DEPENDENCIES.has_key(module):
					dependsOnStr = ','.join(['("%s", "0001_initial")' % dependency for dependency in settings.SOUTH_MIGRATION_DEPENDENCIES[module]])
					os.system('sed -i "" -e "s/%s/%s/g" %s' % ('class Migration\\(SchemaMigration\\):', 'class Migration(SchemaMigration):\\n    depends_on = (%s,)\\n' % dependsOnStr, settings.SOUTH_MIGRATION_MODULES[module].replace('.', '/') + '/0001_initial.py'))
