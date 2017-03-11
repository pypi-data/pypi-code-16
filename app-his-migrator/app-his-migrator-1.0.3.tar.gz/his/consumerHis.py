from django.db import models
import requests
import json
from django.conf import settings

class HisRest(models.Model):

	_url = settings.URL_WS_REST_HIS  

	def post_paciente (self, data):		

		response = requests.post('{0}/paciente/actualizar'.format(self._url), data = json.dumps(data))

		return response.json()

	def post_personal (self, data):

		response = requests.post('{0}/personal/actualizar'.format(self._url), data = json.dumps(data))

		return response.json()

	def post_cita (self, data):

		response = requests.post('{0}/cita/actualizar'.format(self._url), data = json.dumps(data))

		return response.json()
		

