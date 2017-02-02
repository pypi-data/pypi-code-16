from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers import utils as h_utils
from ohm2_handlers.countries import utils
import simplejson as json
import pycountry

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		
		for c in pycountry.countries:
			utils.create_country(code = c.alpha_2, name = c.name)


		self.stdout.write('Finish OK')