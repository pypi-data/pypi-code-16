from ohm2_handlers.definitions import HandlersRunException, HandlersInputException, HandlersMethodException
from . import settings


class CountriesRunException(HandlersRunException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "countries"
		kwargs["save"] = settings.SAVE_RUN_EXCEPTIONS
		super(CountriesRunException, self).__init__(*args, **kwargs)


class CountriesInputException(HandlersInputException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "countries"
		kwargs["save"] = settings.SAVE_INPUT_EXCEPTIONS
		super(CountriesInputException, self).__init__(*args, **kwargs)


class CountriesMethodException(HandlersMethodException):

	def __init__(self, method, address, **kwargs):
		kwargs["app"] = "countries"
		kwargs["save"] = settings.SAVE_METHOD_EXCEPTIONS
		super(CountriesMethodException, self).__init__(method, address, **kwargs)	
		