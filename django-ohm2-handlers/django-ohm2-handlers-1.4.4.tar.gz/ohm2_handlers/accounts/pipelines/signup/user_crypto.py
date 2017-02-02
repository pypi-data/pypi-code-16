from ohm2_handlers.accounts import utils as accounts_utils
import os


def user_crypto(user, request, previous_outputs, *args, **kwargs):
	output = {}
	
	crypto = accounts_utils.get_or_none_crypto(user = user)
	if crypto is None:		
		crypto = accounts_utils.create_crypto(user)

	output["crypto"] = crypto
		
	return (user, output)
