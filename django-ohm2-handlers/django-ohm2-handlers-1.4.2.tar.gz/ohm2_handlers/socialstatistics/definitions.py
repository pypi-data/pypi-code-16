from ohm2_handlers.definitions import HandlersRunException, HandlersInputException, HandlersMethodException
from . import settings


class SocialstatisticsRunException(HandlersRunException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "socialstatistics"
		kwargs["save"] = settings.SAVE_RUN_EXCEPTIONS
		super(SocialstatisticsRunException, self).__init__(*args, **kwargs)


class SocialstatisticsInputException(HandlersInputException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "socialstatistics"
		kwargs["save"] = settings.SAVE_INPUT_EXCEPTIONS
		super(SocialstatisticsInputException, self).__init__(*args, **kwargs)


class SocialstatisticsMethodException(HandlersMethodException):

	def __init__(self, method, address, **kwargs):
		kwargs["app"] = "socialstatistics"
		kwargs["save"] = settings.SAVE_METHOD_EXCEPTIONS
		super(SocialstatisticsMethodException, self).__init__(method, address, **kwargs)	
		