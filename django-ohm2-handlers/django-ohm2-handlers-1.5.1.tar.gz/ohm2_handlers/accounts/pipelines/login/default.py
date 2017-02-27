from ohm2_handlers.accounts import utils as accounts_utils
import os


def default(request, auth_user, previous_outputs, *args, **kwargs):
	output = {}
	
	accounts_utils.user_login(request, auth_user)
	
	return (auth_user, output)
