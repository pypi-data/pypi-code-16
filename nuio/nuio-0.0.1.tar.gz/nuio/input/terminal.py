#!/usr/bin/python3

from .base import BaseInput
import termios, sys, concurrent, asyncio


class POSIXTerminalInput(BaseInput):
	"""
	Get input from a POSIX Terminal/Shell.
	This requires that the terminal can be set to ~ICANON and ~ECHO
	by using termios.

	Some methods will set the correct terminal settings automatically,
	anyways you should set them manually at first.

	All input_* methods, get_string and get_char will require ICANON and ECHO to be set.
	To prevent unpredictable behaviour you should ``reset_tc_attrs``
	before running them.

	get_char_noblock and get_last_char_noblock will require ~ICANON.
	You should ensure to turn it off after you called them if you need
	ICANON.
	"""
	def __init__(self, output):

		BaseInput.__init__(self, output)
		self.stdin_fd = sys.stdin.fileno()
		self._reset_tc_attr = termios.tcgetattr(self.stdin_fd)
		self.tc_attr = termios.tcgetattr(self.stdin_fd)
		self.stdin = sys.stdin		
	
	def set_noICANON(self):
		"""
		Disable ICANON in the terminal

		Returns: None
		"""
		self.tc_attr = termios.tcgetattr(self.stdin_fd)
		self.tc_attr[3] = self.tc_attr[3] & ~termios.ICANON
		termios.tcsetattr(self.stdin_fd, termios.TCSANOW, self.tc_attr)


	def set_noECHO(self):
		"""
		Disable ECHO in the terminal

		Returns: None
		"""
		
		self.tc_attr = termios.tcgetattr(self.stdin_fd)
		self.tc_attr[3] = self.tc_attr[3] & ~termios.ECHO
		termios.tcsetattr(self.stdin_fd, termios.TCSANOW, self.tc_attr)

	def reset_tc_attrs(self):
		"""
		Reset the terminal settings to the original settings

		Returns: None
		"""
		termios.tcsetattr(self.stdin_fd, termios.TCSANOW, self._reset_tc_attr)
	

	async def get_string(self):
		"""
		Resets the terminal attributes and returns input()
		"""
		self.reset_tc_attrs()
		return self.stdin.readline()

	async def get_char(self):
		return self.stdin.read(1)

	def get_char_noblock(self):
		"""
		Sets ~ICANON and reads one char nonblocking.
		"""
		self.set_noICANON()

		# we need to run this in a coroutine...
		# A timeout for the read function
		timeout = 0.002
		loop = asyncio.get_event_loop()
		future = asyncio.wait_for(loop.run_in_executor(None, self.stdin.read, i), timeout)

		try:
			return loop.run_until_complete(future)
		except:
			return None

	def get_last_char_noblock(self):
		"""
		Sets ~ICANON and reads the last entered char nonblocking.
		"""
		self.set_noICANON()
		one_read = False
		char = None
		last_char = None
		while(not one_read and char != None):
			one_read = True
			last_char = char
			char = self.get_char_noblock()

		return last_char

	async def input_char(self, prompt = ""):
		self.output.print(prompt, end = "")
		res = self.stdin.read(1)
		self.output.line_up()
		self.output.print(prompt + res)
		return res

	async def input_string(self, prompt = ""):
		"""
		Sets ICANON and ECHO and prompts the user to enter a string.
		"""
		self.reset_tc_attrs()
		self.output.print(prompt, end = "")
		res = self.stdin.readline()
		self.output.line_up()
		self.output.print(prompt + res)
		return res
	async def input_int(self, prompt = "", range = None):
		"""
		Uses input_string internally.
		"""
		
		def is_valid(integer, range):
			if(integer == None):
				return False
			if(range == None or integer in range):
				return True
			return False

		integer = None
		while(not is_valid(integer, range)):
			string = await self.input_string(prompt = prompt)
			try:
				integer = int(string)
			except:
				continue
		return integer

	async def input_float(self, prompt = "", range = None):
		"""
		Uses input_string internally.
		"""
		
		def is_valid(Float, range):
			if(Float == None):
				return False
			if(range == None or ( range.start < Float < range.stop)):
				return True
			return False

		Float = None
		while(not is_valid(Float, range)):
			string = await self.input_string(prompt = prompt)
			try:
				Float = float(string)
			except:
				continue
		return Float

	async def input_type(self, constructor, prompt = ""):	
		result = None
		while(not result):
			string = await self.input_string(prompt = prompt)
			try:
				result = constructor(string)
			except:
				continue
		return result
	
	
