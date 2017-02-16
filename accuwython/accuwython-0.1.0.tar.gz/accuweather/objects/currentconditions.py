from accuweather_factory import AccuWeatherFactory

'''
	AccuWeather Current Conditions
'''

class AccuWeatherCondition(object):
	
	def __init__(self, accu_id, api):
		self.accu_id = accu_id
		self.endpoint = 'currentconditions'
		self.api = api

	def currentconditions(self):
		full_url = self.api.url_builder(self.endpoint, None, self.accu_id)
		accu_data  = urlopen(full_url)
		
		return json.loads(accu_data.read())



'''
	AccuWeather CurrentConditions Manager
'''

class CurrentConditions(object):

	def __init__(self):
		self.conditions = []

	def __current_factory(self, accu_id, api):
		currentcondition = AccuWeatherFactory.create_object('currentcondition', accu_id, api)
		return currentcondition

	def add_condition(self, accu_id, api):
		currentcondition = self.__current_factory(accu_id, api)
		self.conditions.append(currentcondition)

	def get_temperatures(self,unit_type=None):
		temperatures = []
		
		for condition in self.conditions:

			condition_dict = condition.currentconditions()[0]
			condition_dict['TemperatureMetric'] = condition_dict['Temperature']['Metric']['Value']
			condition_dict['TemperatureImperial'] = condition_dict['Temperature']['Imperial']['Value']
			condition_dict.pop('Temperature', None)

			temperatures.append(condition_dict)

		return temperatures
