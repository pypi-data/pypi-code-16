# vim:set ts=4 sw=4:

import json
import tkinter as tk

class FileParser(object):
	"""
	A simple file parser to import a widget structure from JSON. The only
	notable thing about this is that any key starting with an @-sign will
	have its value replaced with the value of the tk constant the value
	represents (and the @-sign is removed from the key).
	"""
	def parse(self, filename):
		"""
		Parse <filename> and return data structure
		"""
		with open(filename) as fp:
			self.data=json.load(fp)

		self.data=self.replace_tokens(self.data)

		return self.data

	def replace_tokens(self, value):
		"""	
		Recursive replacement of @-token keys and values
		"""
		if isinstance(value, list):
			return [self.replace_tokens(item) for item in value]
		elif isinstance(value, dict):
			result={}
			for k,v in value.items():
				if k.startswith('@'):
					k=k.replace('@', '')
					v=getattr(tk, v)

				result[k]=self.replace_tokens(v)

			return result
		else:
			return value
