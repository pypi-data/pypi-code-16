from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient
from . import settings
from . import utils as h_utils
from .models import BaseError

try:
	import simplejson as json
except Exception:
	import json

class UtilsTestCase(TestCase):

	def setUp(self):
		pass

	def test_send_email(self):

		sent = h_utils.send_html_email(to_email = "slipktonesraton@gmail.com",
									   from_email = "slipktonesraton@gmail.com",
									   subject = "django test send email",
									   html = "<p>HTML</p>")
		

		self.assertEqual(sent, True)



class ApiTestCase(TestCase):

	def setUp(self):
		pass

	def test_create_landing_message(self):
		url = reverse("ohm2_handlers:api_create_landing_message", kwargs = {"version" : "1"})
		
		data = {
			"name" : "name",
			"subject" : "subject",
			"message" : "message"
		}
		
		
		c = APIClient()
		response = c.post(url, data, format = "json")

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(error, False)
		