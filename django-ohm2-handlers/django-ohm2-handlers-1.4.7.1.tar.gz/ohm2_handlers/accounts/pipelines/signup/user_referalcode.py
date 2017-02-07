from ohm2_handlers.accounts import utils as accounts_utils
import os


def user_referalcode(user, request, previous_outputs, *args, **kwargs):
	output = {}
	
	referalcodes = accounts_utils.get_referalcodes(user = user)
	if len(referalcodes) == 0:
		referalcode = accounts_utils.create_referalcode(user)
		output["referalcodes"] = accounts_utils.get_referalcodes(user = user)
		
	else:
		output["referalcodes"] = referalcodes
	
	return (user, output)
