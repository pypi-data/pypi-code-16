from ohm2_handlers.definitions import HandlersRunException, HandlersInputException, HandlersMethodException
from . import settings


class CurrenciesRunException(HandlersRunException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "currencies"
		kwargs["save"] = settings.SAVE_RUN_EXCEPTIONS
		super(CurrenciesRunException, self).__init__(*args, **kwargs)


class CurrenciesInputException(HandlersInputException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "currencies"
		kwargs["save"] = settings.SAVE_INPUT_EXCEPTIONS
		super(CurrenciesInputException, self).__init__(*args, **kwargs)


class CurrenciesMethodException(HandlersMethodException):

	def __init__(self, method, address, **kwargs):
		kwargs["app"] = "currencies"
		kwargs["save"] = settings.SAVE_METHOD_EXCEPTIONS
		super(CurrenciesMethodException, self).__init__(method, address, **kwargs)	
		