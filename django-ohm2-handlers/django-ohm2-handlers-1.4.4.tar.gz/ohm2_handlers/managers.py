from django.db import models
from . import utils as h_utils


class HandlersManager(models.Manager):
	
	def create(self, *args, **kwargs):
		if kwargs.get("identity") is None:
			kwargs["identity"] = h_utils.db_unique_random(self.model)
		return super(HandlersManager, self).create(*args, **kwargs)
	