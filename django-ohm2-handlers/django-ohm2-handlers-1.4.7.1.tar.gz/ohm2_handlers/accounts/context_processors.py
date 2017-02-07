from ohm2_handlers.accounts import utils as accounts_utils

def context(request):
	return {"c_accounts" : accounts_utils.get_context(request)}