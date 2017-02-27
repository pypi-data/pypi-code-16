from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers import utils as h_utils
from ohm2_handlers.currencies import utils
import pycountry


class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		
		currencies = [
			{
				'code' : 'CLP',
				'name' : pycountry.currencies.get(alpha_3 = 'CLP').name,
				'symbol' : '$',
				'decimals' : 0,
			},

			{
				'code' : 'USD',
				'name' : pycountry.currencies.get(alpha_3 = 'USD').name,
				'symbol' : '$',
				'decimals' : 2,
			},

			{
				'code' : 'EUR',
				'name' : pycountry.currencies.get(alpha_3 = 'EUR').name,
				'symbol' : '€',
				'decimals' : 2,
			},
			
		]

		for kwargs in currencies:
			utils.create_currency( **kwargs )
			
		self.stdout.write('Finish OK')
