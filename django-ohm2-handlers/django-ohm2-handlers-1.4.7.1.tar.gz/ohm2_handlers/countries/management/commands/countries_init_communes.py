from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers import utils as h_utils
from ohm2_handlers.countries import utils
import simplejson as json
import os

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		
		
		path = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'BD/JSON/BDCUT_CL_ComunaProvincia.json')
		
		with open(path) as f:
			data = json.load(f) 
			

		
		for k, v in data.items():
			province = utils.get_province(code = k)
			for o in v:
				commune = utils.create_commune(province, o["comuna_id"], o["name"])
				
		self.stdout.write('Finish OK')