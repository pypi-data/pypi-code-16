#!/usr/bin/python3

class BaseOutput(object):
	"""
	Basic output class.
	"""
	def __init__(self):
		pass
	def print(self, *args, end = "\n", sep = " ", flush = False):
		"""
		Print the ``*args`` to the output device.
		Flush might be ignored.

		Returns: None
		"""
		pass

	def print_autowrap(self, *args, end = "\n", sep = " ", flush = False):
		"""
		Print string to the output device. Wrap the string automatically.
		Might default to print in terminals.	

		Returns: None
		"""
		
		pass
	def clear_line(self):
		"""
		Clear the current line. Cannot be used to clear multiple lines.
		Might be done using "\\\\b" or "\\\\r" in terminals.

		Returns: None
		"""
		pass
	def clear_chars(self, numchars):
		"""
		Clear numchars characters. Cannot be used to clear multiple lines.

		Returns: None
		"""
		pass
	def print_colored(self, color, *args, end = "\n", sep = " ", flush = False):
		"""
		Print some colored text. Might support other markup features, too.

		Returns: None
		"""
		pass
	def line_up(self):
		"""
		Goes one line up.

		Returns: None
		"""
		pass
	
		

class BaseBlockOutput(BaseOutput):
	"""
	Used to display stuff in a block.
	Might be used to create screens.
	"""
	
	def __init__(self, height, width):
		self.height = height
		self.width = width
	
	def clear(self):
		"""
		Clear the complete block.

		Returns: None
		"""
		pass
	def goto_line(self, lineno):
		"""
		Go to line ``lineno``. Might raise an exception, if lineno is invalid.
		Will place the cursor at the first character in this line to prevent 
		undefined behaviour.

		Returns: None
		"""
		pass
		

		
	
	
	
			
		
		
