from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers import utils as h_utils
from ohm2_handlers.accounts import utils as accounts_utils
from rest_framework.authtoken.models import Token
import os

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		parser.add_argument('-u', '--username')
		parser.add_argument('-k', '--key')

	def handle(self, *args, **options):
		username = options["username"]
		key = options["key"]
		
		user = accounts_utils.get_user(username = username)
		token = accounts_utils.get_authtoken(user)

		token.delete()

		token = Token.objects.create(user = user, key = key)