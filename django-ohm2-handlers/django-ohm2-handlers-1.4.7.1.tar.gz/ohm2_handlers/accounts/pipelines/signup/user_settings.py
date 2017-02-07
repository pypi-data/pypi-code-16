from ohm2_handlers.accounts import utils as accounts_utils
import os


def user_settings(user, request, previous_outputs, *args, **kwargs):
	output = {}
	
	settings = accounts_utils.get_or_none_settings(user = user)
	if settings is None:
		tmp_sett = {}
		settings = accounts_utils.create_settings(user, **tmp_sett)
	
	output["settings"] = settings
	
	return (user, output)
