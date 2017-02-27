from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from ohm2_handlers import utils as h_utils
from ohm2_handlers import settings as h_settings
from ohm2_handlers.currencies import utils as currencies_utils
from ohm2_handlers.currencies import serializers as currencies_serializers
from ohm2_handlers.currencies import settings
from ohm2_handlers.currencies import errors as currencies_errors
import simplejson as json


class ApiTestCase(TestCase):
	
	test_username = "slipktonesraton@gmail.com"
	test_email = "slipktonesraton@gmail.com"
	test_password = "123123123"	
	

	def setUp(self):
		call_command('currencies_init')
		user = User.objects.create_user(self.test_username, self.test_email, self.test_password)
	
	
	def test_asd(self):
		pass	
	

		