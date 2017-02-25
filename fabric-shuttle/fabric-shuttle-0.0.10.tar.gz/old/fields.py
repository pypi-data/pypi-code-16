from django import VERSION
from django.db import models

from .encryption import encrypt, decrypt

# Note: in 1.8 SubfieldBase is deprecated and from_db_value was added
if VERSION[0] > 1 or VERSION[1] > 7:
	_metaclass = type
else:
	_metaclass = models.SubfieldBase

class EncryptedField(models.CharField):
	__metaclass__ = _metaclass
	description = "An encrypted CharField using AES encryption."

	def __init__(self, *args, **kwargs):
		kwargs['serialize'] = False
		kwargs['editable'] = False
		kwargs['blank'] = True
		kwargs.setdefault('max_length', 255)
		super(EncryptedField, self).__init__(*args, **kwargs)

	def from_db_value(self, value, expression, connection, context):
		if value and value.startswith('AES$'):
			return decrypt(value)
		return value

	def to_python(self, value):
		if value and value.startswith('AES$'):
			return super(EncryptedField, self).to_python(decrypt(value))
		return super(EncryptedField, self).to_python(value)

	def get_prep_value(self, value):
		if value:
			return encrypt(value)
		return value

class EncryptedTextField(models.TextField):
	__metaclass__ = _metaclass
	description = "An encrypted TextField using AES encryption."

	def __init__(self, *args, **kwargs):
		kwargs['serialize'] = False
		kwargs['editable'] = False
		kwargs['blank'] = True
		super(EncryptedTextField, self).__init__(*args, **kwargs)

	def from_db_value(self, value, expression, connection, context):
		if value and value.startswith('AES$'):
			return decrypt(value)
		return value

	def to_python(self, value):
		if value and value.startswith('AES$'):
			return super(EncryptedTextField, self).to_python(decrypt(value))
		return super(EncryptedTextField, self).to_python(value)

	def get_prep_value(self, value):
		if value:
			return encrypt(value)
		return value
