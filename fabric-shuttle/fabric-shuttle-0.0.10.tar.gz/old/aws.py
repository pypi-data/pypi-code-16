import os
import urllib2

from django.conf import settings
from django.contrib.staticfiles import finders

from .colors import bold, red

# NOTE: the path must always end with a /
URL_META_DATA = 'http://169.254.169.254/latest/%s'

def get_user_data():
	"""Get the user-data associated with the current instance."""
	path = URL_META_DATA % 'user-data/'
	return urllib2.urlopen(path).read()

def upload_to_s3(bucket, directory=None, files=None, prefix=None, callback=None):
	"""Uploads files to an s3 bucket.

	Upload either an entire directory with files=None, or specific files with and optional directory prefix.
	If callback is provided it will do a callback for each file uploaded (filename, keyname)
	"""
	
	if bucket is None:
		raise ValueError('Bucket must be specified.')
	if directory is None and files is None:
		raise ValueError('Directory and/or files must be specified.')
	
	# Setup and connect boto
	from boto.s3.connection import S3Connection
	from boto.s3.bucket import Bucket
	from boto.s3.key import Key
	c = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
	k = Key(Bucket(c, bucket))

	# Fix the prefix
	# prefix itself shouldn't have a / prefix itself but should end with /
	if prefix:
		prefix = prefix.lstrip('/')
		if prefix and not prefix.endswith('/'):
			prefix = prefix + '/'

	if files:
		# Upload individual files
		if directory:
			keys = [filename.lstrip('/') for filename in files]
			files = [os.path.join(directory, filename) for filename in files]
		else:
			keys = [os.path.split(filename)[1] for filename in files]
		for i, filename in enumerate(files):
			if prefix:
				k.key = prefix + keys[i]
			else:
				k.key = keys[i]
			if callback:
				callback(filename, k.key)
			k.set_contents_from_filename(filename)
	elif directory:
		# Upload an entire directory
		def __upload(arg, dirname, names):
			# arg is the starting directory
			for name in names:
				filename = os.path.join(dirname, name)
				if not os.path.isdir(filename) and not os.path.islink(filename) and not name.startswith('.'):
					key = filename[len(arg):]
					if key.startswith('/'):
						key = key[1:]
					if prefix:
						key = prefix + key
					k.key = key
					if callback:
						callback(filename, k.key)
					k.set_contents_from_filename(filename)
		os.path.walk(directory, __upload, directory)

def delete_from_s3(bucket, prefix=None, callback=None):
	"""Remove all files with the prefix specified from the bucket."""
	
	if bucket is None:
		raise ValueError('Error: Bucket must be specified.')
	
	# Setup boto
	from boto.s3.connection import S3Connection
	from boto.s3.bucket import Bucket
	from boto.s3.key import Key

	# Fix the prefix
	if prefix:
		prefix = prefix.lstrip('/')

	# Connect to S3, list the contents, and remove all of the keys
	c = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
	b = Bucket(c, bucket)
	result_set = b.list(prefix=prefix)
	if callback:
		for key in result_set:
			callback(key.name)
	result = b.delete_keys([key.name for key in result_set])
