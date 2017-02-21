from ohm2_handlers import utils as h_utils

def context(request):
	return {"c_handlers" : h_utils.get_context(request)}