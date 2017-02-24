import anvil.server


class AppTables:
	cache = None

	def __getattr__(self, name):
		if AppTables.cache is None:
			AppTables.cache = anvil.server.call("anvil.private.tables.get_app_tables")

		tbl = AppTables.cache.get(name)
		if tbl is not None:
			return tbl

		raise AttributeError("No such app table: '%s'" % name)

	def __setattr__(self, name, val):
		raise Exception("app_tables is read-only")

app_tables = AppTables()

def set_client_config(x):
    pass
