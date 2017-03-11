from django.apps import AppConfig
import django.db.models.options as options

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('schemaTramaHis',)

class signalConfig(AppConfig):
	name = 'his'
	verbose_name = 'Signal Application'

	def ready(self):
		import his.mySignal
		
	"""
	def create(cls, entry):
		import django.db.models.options as options
		options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('schema',)
	"""