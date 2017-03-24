def dynamic_import(module,var):
	module = __import__(module,fromlist=[var])
	return getattr(module,var)