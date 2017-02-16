import json

from accuweather import apiconfig
from accuweather import url
from urllib import urlopen, urlencode


'''
	AccuWeather API Url builder
'''

class AccuWeatherApi(object):

	def __init__(self, apikey):
		self.apikey = apikey
		self.base_url = url.AccuWeatherUrl.BASE_URL
		self.version = apiconfig.accuweather_config['API_VERSION']
	

	def url_builder(self, endpoint, params, *args):
		url_details = '/'.join(args)
		encoded_params = self.encode_params(params)

		full_url = '%s/%s/%s/%s?%s' % (self.base_url, endpoint, self.version, url_details, encoded_params)

		return full_url

	def encode_params(self, params=None):
		params_dict = {}
		params_dict['apikey'] = self.apikey

		if params is not None:
			params_dict.update(params)

		encoded_params = urlencode(params_dict)
		
		return encoded_params





if __name__ == '__main__':
	# unittest.main()
	api = AccuWeatherApi('l2wAkfYTeei3nibA0rqqPTozyLQavG5h')
	# peru = AccuWeatherCondition('264120', api)
	# print peru.currentconditions()
	temps = CurrentConditions()
	temps.add_condition('26420', api)
	temps.add_condition('7894', api)
	temps.add_condition('60449', api)
	print(temps.get_temperatures())
	# AccuWeatherFactory.create_object('currentcondition','264120',api)


