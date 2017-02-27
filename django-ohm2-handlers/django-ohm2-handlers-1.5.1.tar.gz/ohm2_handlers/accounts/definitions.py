from ohm2_handlers.definitions import HandlersRunException, HandlersInputException, HandlersMethodException
from . import settings


class AccountsRunException(HandlersRunException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "accounts"
		kwargs["save"] = settings.SAVE_RUN_EXCEPTIONS
		super(AccountsRunException, self).__init__(*args, **kwargs)


class AccountsInputException(HandlersInputException):

	def __init__(self, *args, **kwargs):
		kwargs["app"] = "accounts"
		kwargs["save"] = settings.SAVE_INPUT_EXCEPTIONS
		super(AccountsInputException, self).__init__(*args, **kwargs)


class AccountsMethodException(HandlersMethodException):

	def __init__(self, method, address, **kwargs):
		kwargs["app"] = "accounts"
		kwargs["save"] = settings.SAVE_METHOD_EXCEPTIONS
		super(AccountsMethodException, self).__init__(method, address, **kwargs)	
		