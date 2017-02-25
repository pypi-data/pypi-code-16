from optparse import make_option
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = 'Reset the database to just initial data, also calls resetmigrations. Only to be used on development sqlite databases.'
	option_list = BaseCommand.option_list + (
			make_option('--preserve', '-p',
				action='store_true',
				dest='preserve',
				default=False,
				help='Preserve the database data through resyncing, remigrating.'),
		)

	def handle(self, *args, **options):
		if not hasattr(settings, 'DEBUG') or not settings.DEBUG:
			print 'This command is only valid for development, DEBUG is not True.'
			return
		if settings.DATABASES['default']['ENGINE'].find('sqlite') == -1:
			print 'This command is only valid for development with sqlite databases.'
			return
		import pdb; pdb.set_trace()
		file = settings.DATABASES['default']['NAME']
		dataFile = file + '.json'
		if options['preserve']:
			os.system('python manage.py dumpdata --exclude south --exclude contenttypes --exclude auth.Permission --exclude admin.LogEntry > %s' % dataFile)
		call_command('resetmigrations')
		os.system('rm %s' % file)
		if options['preserve']:
			os.system('python manage.py syncdb --noinput --no-initial-data')
			os.system('python manage.py migrate --noinput --no-initial-data')
			call_command('loaddata', dataFile)
			os.system('rm %s' % dataFile)
		else:
			os.system('python manage.py syncdb --noinput')
			os.system('python manage.py migrate --noinput')
