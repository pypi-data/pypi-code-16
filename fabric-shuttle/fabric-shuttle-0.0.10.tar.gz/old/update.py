from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.db.models.fields import FieldDoesNotExist
from django.db.models.loading import cache

# These methods are most useful for logging and updating a stats model about an instance

def update_fields(instance, updates, select=False):
	"""Tries to update fields for an instance.

	Instance will not be updated upon return reflecting the updates!
	pre_ and post_save signals will not be sent when using this method!
	Use a normal select_for_update().get(), save() if the above is needed.
	select=True will give you pre_ post_save signals, but instance will not be updated.
	Only use update within an app with private fields and no signals are needed.
	"""
	if instance is None:
		return
	model = instance.__class__
	
	if select:
		try:
			select_instance = model.object.select_for_update().get(id=instance.id)
			for field_name in updates.keys():
				if hasattr(select_instance, field_name):
					setattr(select_instance, field_name, getattr(select_instance, field_name) + updates[field_name])
			select_instance.save()
		except ObjectDoesNotExist:
			pass
	else:
		# Do an actual update by resolving the updates into fields
		update_args = {}
		for field_name in updates.keys():
			try:
				field = model._meta.get_field_by_name(field_name)
				update_args[field_name] = F(field_name) + updates[field_name]
			except FieldDoesNotExist:
				pass
	
		if len(update_args):
			model.objects.filter(**{'id': instance.id}).update(**update_args)

def update_related_fields(model, related_field, related_instance, updates, select=False):
	"""Tries to update fields for a related instance.

	Take the same precautions as noted for the above update_fields.
	Optionally, pass select=True to use select_for_update and get the expected pre_ post_save signals.
	"""
	if model is None or related_instance is None:
		return
	if type(model) is str:
		modelStr = model.split('.')
		model = cache.get_model(modelStr[0], modelStr[1])
		
	if select:
		# Do the select_for_update
		try:
			instance = model.object.select_for_update().get(**{related_field: related_instance})
			for field_name in updates.keys():
				if hasattr(instance, field_name):
					setattr(instance, field_name, getattr(instance, field_name) + updates[field_name])
			instance.save()
		except ObjectDoesNotExist:
			pass
	else:
		# Do an actual update by resolving the updates into fields
		update_args = {}
		for field_name in updates.keys():
			try:
				field = model._meta.get_field_by_name(field_name)
				update_args[field_name] = F(field_name) + updates[field_name]
			except FieldDoesNotExist:
				pass
	
		if len(update_args):
			model.objects.filter(**{related_field: related_instance}).update(**update_args)
