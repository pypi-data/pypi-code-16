
'''
	AccuWeather Object Factory
'''

class AccuWeatherFactory(object):

	accu_types = {'currentcondition':AccuWeatherCondition}

	@classmethod
	def create_object(cls, accu_type, accu_id, api):
		return cls.accu_types[accu_type](accu_id, api)
