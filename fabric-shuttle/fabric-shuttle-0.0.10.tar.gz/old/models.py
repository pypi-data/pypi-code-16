import os
import shutil
import tempfile

from django.conf import settings
from django.core.urlresolvers import resolve
from django.test.client import RequestFactory

def abstract_model_copy(model, exclude=None):
	"""Returns a copy of a model to be used as an abstract base class."""
	attrs = {}
	for field in model._meta.fields:
		if field.name != 'id' and field.name not in exclude:
			attrs[field.name] = field
	attrs['__module__'] = model.__module__
	attrs['Meta'] = type('Meta', (), {'abstract':True})
	copy = type(model.__name__ + 'Copy', model.__bases__, attrs)
	return copy

def have_fields_changed(obj, *fields):
	"""Returns True if all the specified fields on an object have changed compared the current database version."""
	if not obj.pk:
		return False
	try:
		current_obj = obj.__class__.objects.only(*fields).get(pk=obj.pk)
		for field in fields:
			if getattr(obj, field) == getattr(current_obj, field):
				return False
		return True
	except:
		return False

def __publish_object(obj, unpublish=False, callback=None):
	if not hasattr(obj, 'get_absolute_url'):
		raise ValueError('%s is not setup for publishing' % repr(obj))
	if hasattr(obj.__class__, 'Publishing'):
		publishing = obj.__class__.Publishing
	else:
		publishing = None
	# Configure the publish and unpublish methods
	slug_field = getattr(publishing, 'slug_field', 'slug')
	slug = getattr(obj, slug_field, str(obj.pk))
	prefix = getattr(publishing, 'prefix', '')
	if not prefix.endswith('/'):
		prefix = '%s/%s/' % (prefix.lstrip('/'), slug)
	else:
		prefix = '%s%s/' % (prefix.lstrip('/'), slug)
	kwargs = {'callback': callback, 'prefix': prefix}
	if hasattr(settings, 'AWS_ACCESS_KEY_ID') and hasattr(settings, 'AWS_SECRET_ACCESS_KEY'):
		from aws import upload_to_s3, delete_from_s3
		upload = upload_to_s3
		delete = delete_from_s3
		kwargs['bucket'] = getattr(publishing, 'bucket', settings.AWS_STORAGE_BUCKET_NAME)
	else:
		raise Exception('No publishing data store is available')
		
	if unpublish:
		# Unpublishing (deleting)
		delete(**kwargs)
		obj.update(published=None)
	else:
		# Publishing
		tempdir = tempfile.mkdtemp()
		rf = RequestFactory()
		url = obj.get_absolute_url()
		request = rf.get(url)
		view, view_args, view_kwargs = resolve(url)
		response = view(request, *view_args, **view_kwargs)
		# If the url has no extension, the convert it to index.html
		if not len(os.path.splitext(url)[1]):
			filename = '%s/index.html' % tempdir
		else:
			filename = os.path.join(tempdir, url.strip('/'))
		with open(filename, 'w') as f:
			f.write(response.content if not response.streaming else b''.join(response.streaming_content))
		subpages = getattr(publishing, 'subpages', [])
		for subpage in subpages:
			url = os.path.join(obj.get_absolute_url(), subpage)
			request = rf.get(url)
			view, view_args, view_kwargs = resolve(url)
			response = view(request, *view_args, **view_kwargs)
			if not len(os.path.splitext(subpage)[1]):
				filename = '%s/index.html' % os.path.join(tempdir, subpage.strip('/'))
			else:
				filename = os.path.join(tempdir, subpage.strip('/'))
			try:
				os.makedirs(os.path.split(filename)[0])
			except:
				pass
			with open(filename, 'w') as f:
				f.write(response.content if not response.streaming else b''.join(response.streaming_content))
		upload(directory=tempdir, **kwargs)
		shutil.rmtree(tempdir)

def publish_object(obj, callback=None):
	"""Publish or delete an object onto a production data store.

	An object's get_absolute_url method MUST be implemented. index.html will be appended to any url ending with /
	NOTE: When publishing from a development command be sure to sync media files and the object itself (sync_data and sync_media) and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY need to be in the development settings.
		model.Publishing values:
			prefix - the prefix to use on all uploaded files, default is ''
			slug_field - the obj attribute to use as the unique path under prefix, default is slug
			subpages - list of subpages to render and publish: urls relative to this object's get_absolute_url() e.g. subpage/
			bucket - for S3 only, the bucket to use
	"""
	__publish_object(obj, callback=callback)

def unpublish_object(obj, callback=None):
	__publish_object(obj, True, callback=callback)

def sync_objects(queryset, other_database='default'):
	"""Sync data between one database and another from a queryset. Will also sync any select_related data."""
	def __sync_related(obj, related_dict):
		# Recursively save the related objects
		for field in related_dict:
			related_obj = getattr(obj, field)
			related_obj.save(using=other_database)
			if related_dict[field]:
				__sync_related(related_obj, related_dict[field])

	for obj in queryset:
		# query.select_related will equal either False or e.g. {'field': {'subfield': {}}} for select_related('field__subfield')
		if queryset.query.select_related:
			__sync_related(obj, queryset.query.select_related)
		obj.save(using=other_database)

# Media methods should be used within management commands only

def __load_production_default_storage(production_settings):
	production_settings_module = __import__(production_settings, globals(), locals(), ['DEFAULT_FILE_STORAGE'], -1)
	file_storage_class = production_settings_module.DEFAULT_FILE_STORAGE
	file_storage_class = file_storage_class.split('.')
	file_storage_module = __import__('.'.join(file_storage_class[:-1]), globals(), locals(), [file_storage_class[-1]], -1)
	file_storage_class = getattr(file_storage_module, file_storage_class[-1])
	file_storage = file_storage_class()
	return file_storage

def __sync_media(media_files, src_storage, dest_storage, ignore_missing, callback):
	"""Saves media from src_storage into dest_storage."""
	for media_file in media_files:
		if not ignore_missing and not src_storage.exists(media_file):
			raise IOError('No such file %s' % media_file)
		elif callback:
			callback(media_file)
		f = src_storage.open(media_file)
		dest_storage.delete(media_file)
		dest_storage.save(media_file, f)
		f.close()

def upload_media(media_files, production_settings, ignore_missing=True, callback=None):
	"""
	Upload a subset of media files to the production data store. Both the development and production DEFAULT_FILE_STORAGE classes are used.
	Appropriate access keys etc. will need to also be defined in development settings.
	"""
	if media_files:
		from django.core.files.storage import default_storage
		production_default_storage = __load_production_default_storage(production_settings)
		__sync_media(media_files, default_storage, production_default_storage, ignore_missing, callback)

def download_media(media_files, production_settings, ignore_missing=True, callback=None):
	"""
	Download a subset of media files from a production data store. Both the development and production DEFAULT_FILE_STORAGE classes are used.
	Appropriate access keys etc. will need to also be defined in development settings.
	"""
	if media_files:
		from django.core.files.storage import default_storage
		production_default_storage = __load_production_default_storage(production_settings)
		__sync_media(media_files, production_default_storage, default_storage, ignore_missing, callback)
