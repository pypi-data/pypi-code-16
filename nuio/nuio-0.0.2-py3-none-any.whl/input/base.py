#!/usr/bin/python3

class BaseInput(object):
	"""
	Base input class. Used to get user input.

	output is used to prompt the user for input.

	output might be an instance of nuio.output.base.BaseOutput
	or a simple instance like that:

	>>> class OutputDevice(object):
	... 	def __init__(self):
	... 		pass
	... 	def print(self, *args, **kwargs):
	... 		print(*args, **kw_args)
	... 	def line_up(self):
	... 		print("\\r\\033[A", end = "")
	"""
	def __init__(self, output):
		self.output = output
	async def get_string(self):
		"""
		Get an input string. Wait for the user to finish the input.

		Returns: the string
		"""
		pass
	async def get_char(self):
		"""
		Get an input character. Wait for the user to finish the input.
		This might require a terminal '\\\\n'.

		Returns: the character
		"""
		pass
	def get_char_noblock(self):
		"""
		Get an input character. Do not wait for the user to finish the input.
		Might set the terminal to ``~ICANON`` and ``~ECHO``.
		This will return the first character.

		Returns: character or None
		"""
		pass
	def get_last_char_noblock(self):
		"""
		Just like get_char_noblock, but this will return the last character.

		Returns: character or None
		"""
		pass

	async def input_char(self, prompt = ""):
		"""
		Prompt the user to enter a character.

		Returns: the character
		"""
		pass
	async def input_string(self, prompt = ""):
		"""
		Prompt the user to enter a string.

		Returns: the string
		"""
		pass
	async def input_int(self, prompt = "", range = None):
		"""
		Prompt the user to enter an integer.
		It will loop until the entered integer is valid.

		Returns: the integer
		"""
		pass
	async def input_float(self, prompt = "", range = None):
		"""
		Prompt the User to enter a float.
		It will loop until the entered float is valid.

		Returns: the float
		"""
		pass

	async def input_type(self, constructor, prompt = ""):	
		"""
		Promt the user to enter a custom type.
		This will loop until the constructor returns
		something not-None and raises no exceptions.

		Example:

		>>> i = BaseInput()
		>>> def get_positive_integer(string):
			i = int(string)
			if(i > 0):
				return i
			return None
		>>> i.input_type(get_positive_integer, prompt = "enter a positive integer > ")	

		Returns: Instance of the custom type
		"""
		pass
		
		
	
