from ohm2_handlers.accounts import utils as accounts_utils
import os


def user_avatars(user, request, previous_outputs, *args, **kwargs):
	output = {}
	
	avatars = accounts_utils.get_or_none_avatars(user = user)
	if avatars is None:
		tmp_sett = {}
		avatars = accounts_utils.create_avatars(user, **tmp_sett)
	
	output["avatars"] = avatars

	return (user, output)
