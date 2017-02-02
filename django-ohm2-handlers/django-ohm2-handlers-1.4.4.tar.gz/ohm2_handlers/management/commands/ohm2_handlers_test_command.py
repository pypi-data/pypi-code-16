from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from ohm2_handlers import utils as h_utils
from ohm2_handlers import models as handlers_models


class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		
		"""
		be = h_utils.db_create(handlers_models.BaseError, last_update = timezone.now())

		print(be.identity)

		"""

		image = h_utils.get_local_image("/Users/tonra/Downloads/Lg_logo-6.jpg")

		print(image.size,image.name)