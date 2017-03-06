import json
import requests
from uuid import uuid4
import platform 
import sys
import datetime
import urllib

BASE_URL = "https://api.taplytics.com"
EVENT_BASE_URL = "https://ping.taplytics.com"

APP_USER_KEY = 'a4cbf0842807b43a0000'
VALID_ATTRIBUTES = set(['email', 'user_id', 'firstName', 'lastName', 'name', 'age', 'gender', 'customData', 'avatarUrl'])

class Client():

	def __init__(self,sdk_key,os_name=None,os_version=None,lang=None,lang_version=None):

		################### SET CLASS ATTRIBUTES, GET PLATFORM DETAILS #####################################
		#also convert all user given variables to strings, just incase.

		self.sdk_key = str(sdk_key)
		self.sdk_version = str('0.0.3')

		#get OS name and version
		if os_name == None:
			self.os_name = platform.system()
		else:
			self.os_name=str(os_name)

		if os_version == None:
			self.os_version = platform.version()
		else:
			self.os_version = str(os_version)
		
		self.session_id=''

		#get python version
		if lang == None:
			self.lang = 'python'
		else:
			self.lang = str(lang)

		if lang_version == None:
			version = sys.version_info
			self.lang_version = str(version[0]) + '.' +str(version[1]) + '.' + str(version[2])
		else:
			self.lang_version = str(lang_version)
		
		#this variables are always 0 in this release
		self.ab = '0'
		self.av = '0'
		self.config = None
		self.user_id = None

	def create_ad_from_userid(self,user_id):
		#prepend sdk key to user id
		return(str(self.sdk_key) + '-' + str(user_id))

	def generate_param_object(self):
		params = {}
		params['userAgent'] = self.os_name + '%' + self.os_version + '%' + self.lang + '%' + self.lang_version
		return(params)

	# Construct the base params for making requests to the API
	def base_request_params(self, user_id):
		config_params = self.generate_param_object()

		get_params = {
			"sdk": self.sdk_version,
			"t": self.sdk_key,
			"os": 'server',
			"ad": self.create_ad_from_userid(user_id),
			"ab": self.ab,
			"av": self.av,
			"prms": json.dumps(config_params)
		}
		return(get_params)

	#made it into seperate functions incase there needs to be further parsing done in the future
	def parse_variation_check(self,response):
		expN = response.get('expN', {})
		return(expN)

	#made it into seperate functions incase there needs to be further parsing done in the future
	def parse_dynamic_variables(self,response):
		dyn_vars = response.get('dynamicVars', {})
		return(dyn_vars)

	#Gets response from TL API and stores in class as attribute
	def getConfig(self, user_id, new_session=False):

		params = self.base_request_params(user_id)
		
		if(not new_session):
			# if (self.session_id and len(self.session_id) > 0):
			# 	params['sid'] = self.session_id
			# else:
			params['uls'] = 'true'

		try:
			response = requests.get(BASE_URL + '/api/v1/clientConfig', params=params)
			status = response.status_code
		except Exception as e:
			raise e

		if status != 200:
			print "Error with data fetching"

		self.config = response.json()
		self.session_id= self.config.get('sid')
		return(response)

	def startNewSession(self, user_id):
		self.getConfig(user_id, new_session=True)

	def getVariationForExperiment(self, expname, user_id):
		if not self.config or not self.user_id or user_id != self.user_id:
			self.getConfig(user_id)
			self.user_id = user_id
			
		variation = ''
		expN = self.parse_variation_check(self.config)

		for i in expN:
			if i['e'] == expname:
				variation = i['v']

		return(variation)

	def getValueForVariable(self, varName, default, user_id):
		if not self.config or not self.user_id or user_id != self.user_id:
			self.getConfig(user_id)
			self.user_id = user_id
		dyn_vars = self.parse_dynamic_variables(self.config)

		if(dyn_vars.get(varName, None) != None):
			return(dyn_vars[varName]['value'])
		else:
			return default

	def sendEvent(self, name, user_id, value=None, metaData=None):
		body = self.base_request_params(user_id)
		e = []
		event = {}
		event['gn'] = name
		event['type'] = 'goalAchieved'
		event['prod'] = 1
		event['date'] = datetime.datetime.now().replace(microsecond=0).isoformat()
		if value != None:
			event['value'] = value
		if metaData != None:
			event['metaData'] = metaData
		e.append(event)
		body['e']= e
		body['uls'] = True

		response = requests.post(EVENT_BASE_URL + '/api/v1/clientEvents', json=body)
		return(response.status_code)

	def setUserAttributes(self, user_id, attributes={}):
		difference = [a for a in attributes.keys() if a not in VALID_ATTRIBUTES]
		
		if (len(difference) > 0 and not attributes.get('customData')):
			attributes['customData'] = {}
			for item in difference:
				attributes['customData'][item] = attributes[item]
				del attributes[item]

		body = self.base_request_params(user_id)
		body['t'] = self.sdk_key
		body['k'] = APP_USER_KEY
		body['au'] = attributes
		body['os'] = 'server'
		body['uls'] = True

		response = requests.post(BASE_URL + '/api/v1/clientAppUser', json=body)
		return(response.status_code)




