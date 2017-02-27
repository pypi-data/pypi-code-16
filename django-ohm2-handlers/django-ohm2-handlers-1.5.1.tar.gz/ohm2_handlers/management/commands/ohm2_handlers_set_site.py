from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site



class Command(BaseCommand):
	
	def add_arguments(self, parser):
		parser.add_argument('-d', '--domain')

	def handle(self, *args, **options):
		domain = options["domain"]
		site = Site.objects.get_current()
		site.domain = domain
		site.save()
		pass
