from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from ohm2_handlers import utils as h_utils
from ohm2_handlers import settings as h_settings
from ohm2_handlers.countries import utils as countries_utils
from ohm2_handlers.countries import serializers as countries_serializers
from ohm2_handlers.countries import settings
from ohm2_handlers.countries import errors as country_errors
import simplejson as json


class ApiTestCase(TestCase):
	
	test_username = "slipktonesraton@gmail.com"
	test_email = "slipktonesraton@gmail.com"
	test_password = "123123123"	
	

	def setUp(self):
		#countries_utils.create_country(code = "CL", name = "Chile")
		call_command('countries_init')
		call_command('countries_init_regions')
		user = User.objects.create_user(self.test_username, self.test_email, self.test_password)
	
	def test_get_flag_code(self):
		
		url = reverse("countries:api_flag_code", kwargs = {"version" : "1"})
		data = {
			"s" : "32",
			"f" : "cl.png"
		}		
		
		c = APIClient()
		response = c.get(url, data)
		

		self.assertEqual(response.status_code, 200)


	def test_get_country(self):
		
		url = reverse("countries:api_get_country", kwargs = {"version" : "1"})
		
		data = {
			"c" : "CL",
		}
		
		
		c = APIClient()
		c.login(username = self.test_username, password = self.test_password)

		response = c.post(url, data, format = "json")
		

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(error, False)


	def test_get_regions(self):
		
		url = reverse("countries:api_get_regions", kwargs = {"version" : "1"})
		
		data = {
			"country" : "CL"
		}
		
		
		c = APIClient()
		c.login(username = self.test_username, password = self.test_password)

		response = c.post(url, data, format = "json")
		

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(error, False)


	
		
	

		