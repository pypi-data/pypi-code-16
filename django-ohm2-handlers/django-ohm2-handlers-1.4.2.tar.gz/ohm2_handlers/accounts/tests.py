from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.management import call_command
from ohm2_handlers import utils as h_utils
from ohm2_handlers import settings as h_settings
from ohm2_handlers.currencies import utils as currencies_utils
from ohm2_handlers.countries import utils as countries_utils
from ohm2_handlers.accounts import utils as accounts_utils
from ohm2_handlers.accounts import serializers as accounts_serializers
from ohm2_handlers.accounts import settings
from ohm2_handlers.accounts import errors as accounts_errors
import simplejson as json

							 	
class ApiTestCase(TestCase):
	
	test_username = "testusername"
	test_email = "slipktonesraton@gmail.com"
	test_password = h_utils.random_string(10)
	test_alias = "testalias"

	test_long_email = h_utils.random_string(30) + "@fakedomain.com"
	test_long_email_password = h_utils.random_string(10)

	test_email_2 = "oliverherreram@gmail.com"
		
	def setUp(self):
		h_settings.PRINT_BASE_ERRORS = False

		call_command('countries_init')
		call_command('currencies_init')

		user = accounts_utils.create_user(self.test_username, self.test_email, self.test_password)		
		

	def test_signup_success(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = True	

		c = Client()
		url = reverse("accounts:api_signup", kwargs = {"version" : "1"})
		
		data = {
			"username" : h_utils.random_string(10),
			"password" : h_utils.random_string(10),
			"email" : "asd@asd.com",
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)	
		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL
		
			


	def test_login_by_username_success(self):
		ENABLE_ALIAS_LOGIN_ORIGINAL = settings.ENABLE_ALIAS_LOGIN
		settings.ENABLE_ALIAS_LOGIN = False

		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_username,
			"password" : self.test_password,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, not res["ret"])	


		settings.ENABLE_ALIAS_LOGIN = ENABLE_ALIAS_LOGIN_ORIGINAL



	
	def test_logout_by_username_success(self):
		ENABLE_ALIAS_LOGIN_ORIGINAL = settings.ENABLE_ALIAS_LOGIN
		settings.ENABLE_ALIAS_LOGIN = False

		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_username,
			"password" : self.test_password,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, not res["ret"])	






		url = reverse("accounts:api_logout", kwargs = {"version" : "1"})
		
		data = {
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, not res["ret"])

		settings.ENABLE_ALIAS_LOGIN = ENABLE_ALIAS_LOGIN_ORIGINAL	