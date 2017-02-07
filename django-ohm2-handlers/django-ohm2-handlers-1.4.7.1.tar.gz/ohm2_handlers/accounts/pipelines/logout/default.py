from ohm2_handlers.accounts import utils as accounts_utils
import os


def default(request, previous_outputs, *args, **kwargs):
	output = {}
	
	accounts_utils.user_logout(request)
	
	return output
