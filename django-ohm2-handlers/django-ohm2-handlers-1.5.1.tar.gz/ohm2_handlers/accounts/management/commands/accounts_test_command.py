from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers import utils as h_utils
from accounts import utils as accounts_utils
import os

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		pass
