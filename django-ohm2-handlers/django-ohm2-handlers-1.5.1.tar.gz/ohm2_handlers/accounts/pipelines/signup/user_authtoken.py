from ohm2_handlers.accounts import utils as accounts_utils
import os


def user_authtoken(user, request, previous_outputs, *args, **kwargs):
	output = {}
	
	output["authtoken"] = accounts_utils.get_or_create_authtoken(user)
	
	return (user, output)
