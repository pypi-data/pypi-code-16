from ohm2_handlers.accounts import utils as accounts_utils
import os


def user_keys(user, request, previous_outputs, *args, **kwargs):
	output = {}
	
	keys = accounts_utils.get_or_none_keys(user = user)
	if keys is None:
		keys = accounts_utils.create_keys(user)
	
	output["keys"] = keys

	return (user, output)
