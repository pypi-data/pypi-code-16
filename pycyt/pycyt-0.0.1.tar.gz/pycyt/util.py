"""Utility functions and classes."""

from collections import Mapping


class FrozenDict(Mapping):
	"""Immutable mapping class."""

	def __init__(self, *args, **kwargs):
		self._dict = dict(*args, **kwargs)
		self._hash = None

	def __iter__(self):
		return iter(self._dict)

	def __len__(self):
		return len(self._dict)

	def __getitem__(self, key):
		return self._dict[key]

	def __hash__(self):
		if self._hash is None:
			self._hash = hash(frozenset(self._dict.items()))
		return self._hash

	def keys(self):
		return self._dict.keys()

	def values(self):
		return self._dict.values()

	def items(self):
		return self._dict.items()

	def get(self, key, default=None):
		return self._dict.get(key, default)

	def __repr__(self):
		return '{}({})'.format(type(self).__name__, self._dict)
