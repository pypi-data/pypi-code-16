#!/usr/bin/python3

"""
Terminal output devices.

There are a bunch of ANSI escape sequences that might be used by
TerminalOutput.print_colored in ``ESCAPES``.

However you should use ``colors`` for a more compatible version.

Example:

>>> out = TerminalOutput()
>>> out.print_colored(ESCAPES["fg_red"], "this is a test")
this is a test
>>> # this was red
>>> out.print_colored(colors["bg_blue"], "This will have a blue bg")
This will have a blue bg
>>> out.print_colored(colors["bg_white"] + colors["fg_black"], "This will be black on white")
This will be black on white


See nuio.output.base for all common methods.
"""

from .base import BaseOutput, BaseBlockOutput
import sys


ESCAPES = {\
"end": "\033[0m",
"bold": "\033[1m",
"faint": "\033[2m",
"italic": "\033[3m",
"underline": "\033[4m",
"framed": "\033[51m",
"encircled": "\033[52m",


"fg_black":   "\033[30m",
"fg_red":     "\033[31m",
"fg_green":   "\033[32m",
"fg_yellow":  "\033[33m",
"fg_blue":    "\033[34m",
"fg_magenta": "\033[35m",
"fg_cyan":    "\033[36m",
"fg_white":   "\033[37m",

"bg_black":   "\033[40m",
"bg_red":     "\033[41m",
"bg_green":   "\033[42m",
"bg_yellow":  "\033[43m",
"bg_blue":    "\033[44m",
"bg_magenta": "\033[45m",
"bg_cyan":    "\033[46m",
"bg_white":   "\033[47m",

"fg_high_black":   "\033[90m",
"fg_high_red":     "\033[91m",
"fg_high_green":   "\033[92m",
"fg_high_yellow":  "\033[93m",
"fg_high_blue":    "\033[94m",
"fg_high_magenta": "\033[95m",
"fg_high_cyan":    "\033[96m",
"fg_high_white":   "\033[97m",

"bg_high_black":   "\033[100m",
"bg_high_red":     "\033[101m",
"bg_high_green":   "\033[102m",
"bg_high_yellow":  "\033[103m",
"bg_high_blue":    "\033[104m",
"bg_high_magenta": "\033[105m",
"bg_high_cyan":    "\033[106m",
"bg_high_white":   "\033[107m"
}

colors = {\
"fg_black":   "\033[30m",
"fg_red":     "\033[31m",
"fg_green":   "\033[32m",
"fg_yellow":  "\033[33m",
"fg_blue":    "\033[34m",
"fg_magenta": "\033[35m",
"fg_cyan":    "\033[36m",
"fg_white":   "\033[37m",

"bg_black":   "\033[40m",
"bg_red":     "\033[41m",
"bg_green":   "\033[42m",
"bg_yellow":  "\033[43m",
"bg_blue":    "\033[44m",
"bg_magenta": "\033[45m",
"bg_cyan":    "\033[46m",
"bg_white":   "\033[47m",

"fg_high_black":   "\033[90m",
"fg_high_red":     "\033[91m",
"fg_high_green":   "\033[92m",
"fg_high_yellow":  "\033[93m",
"fg_high_blue":    "\033[94m",
"fg_high_magenta": "\033[95m",
"fg_high_cyan":    "\033[96m",
"fg_high_white":   "\033[97m",

"bg_high_black":   "\033[100m",
"bg_high_red":     "\033[101m",
"bg_high_green":   "\033[102m",
"bg_high_yellow":  "\033[103m",
"bg_high_blue":    "\033[104m",
"bg_high_magenta": "\033[105m",
"bg_high_cyan":    "\033[106m",
"bg_high_white":   "\033[107m"
}


class TerminalOutput(BaseOutput):
	"""
	Terminal output device.
	Currently compatible to POSIX terminals.
	"""
	def __init__(self):
		pass
	def print(self, *args, end = "\n", sep = " ", flush = False):
		print(*args, end = end, sep = sep, flush = flush)

	def print_autowrap(self, *args, end = "\n", sep = " ", flush = False):
		print(*args, end = end, sep = sep, flush = flush)

	def print_colored(self, color, *args, end = "\n", sep = " ", flush = False):
		"""
		Print some colored text to the terminal. Actually you are able to
		use any ASCII escape sequence.		

		All colors are in the dict ``colors``. All used escape sequences are in ``ESCAPES``.

		Returns: None
		"""
		print(color, end = "")
		print(*args, end = "", sep = sep, flush = flush)
		print(ESCAPES["end"], end = end, flush = flush)
	def clear_line(self):
		"""
		This is a brute force approach. It will put 100 "\\\\b" and
		one "\\\\r" in the hope that it will be enough.
		"""
		print("\b" * 100, end = "")
		print("\r", end = "")

	def clear_chars(self, numchars):
		print("\b" * numchars, end = "")
	def line_up(self):
		print("\r\033[A", end = "")
		


	
class TerminalBlockOutput(BaseBlockOutput):
	"""
	A block oriented output device with 
	``height`` lines and ``width`` characters.

	*Note*: This buffers the complete output that might be visible.
	If you want to clear this buffer, use ``TerminalBlockOutput.clear``.
	To clear the screen without deleting the buffer use ``TerminalBlockOutput.clear_screen``.

	"""
	def __init__(self, height, width):
		self.height = height
		self.width = width
		self.cursor = [0, 0]
		self.content = []
	def print(self, *args, end = "\n", sep = " ", flush = False):
		"""
		Alias of print_autowrap.
		"""
		self.print_autowrap(*args, end = end, sep = sep, flush = flush)

	def print_autowrap(self, *args, end = "\n", sep = " ", flush = False):
		"""
		This will break lines, if they are too long
		and scroll lines if there are too many lines for the 
		block.
		"""
		string = sep.join([str(arg) for arg in args]) + end
		lines = string.split("\n")
		wraped_lines = []
		for line in lines:
			if(line == ""):
				continue
			while(len(line) > self.width):
				wraped_lines.append(line[:self.width])
				line = line[self.width:]
			wraped_lines.append(line)
		after = self.content[self.cursor[0] + len(wraped_lines):]
		before = self.content[:self.cursor[0]]
		self.content = before + wraped_lines + after
		if(len(self.content) > self.height):
			self.content = self.content[-1 * self.height: ]
		self.clear_screen()
		self.cursor[0] = len(self.content)
		self.cursor[1] = len(self.content[-1])
		print("\n".join(self.content), flush = flush, end = end)
		if("\n" in end):
			self.cursor[0] += end.count("\n")



	def print_colored(self, color, *args, end = "\n", sep = " ", flush = False):
		"""
		Adds ``color`` and ``ESCAPES["end"]`` to the args and invokes
		print_autowrap.
		"""
		args = list(args)
		args = [color] + args + [ESCAPES["end"]]
		self.print_autowrap(*args, end = end, sep = sep, flush = flush)

	def clear_line(self):
		"""
		Will clear the current line
		"""
		print("\b" * self.cursor[1], end = "")
		self.cursor[1] = 0

	def clear_chars(self, numchars):
		print("\b" * numchars, end = "")
		self.cursor[1] -= numchars
		if(self.cursor[1] < 0):
			self.cursor[1] = 0

	def clear(self):
		"""
		Clear the complete block.

		Returns: None
		"""
		self.clear_screen()
		self.content = []
		self.cursor = [0, 0]
	def goto_line(self, lineno):
		"""
		Go to line ``lineno``. Might raise an exception, if lineno is invalid.
		Will place the cursor at the first character in this line to prevent 
		undefined behaviour.

		Returns: None
		"""
		if(self.cursor[0] < lineno):
			print("\r\n" * (lineno - self.cursor[0]), end = "")
		elif(self.cursor[0] > lineno):
			print("\r" + "\033[A" * (self.cursor[0] - lineno), end = "")
		print("\r", end = "")
		self.cursor[1] = 0
		self.cursor[0] -= self.cursor[0] - lineno

	def clear_screen(self):
		"""
		Clear the complete screen.

		Returns: None
		"""
		print("\r" + "\033[A" * (self.cursor[0]), end = "")
		print(( " " * self.width + "\n" )* self.height, end = "")
		print("\r" + "\033[A" * (self.height), end = "")
	def line_up(self):
		self.goto_line(self.cursor[0] - 1)

	
	
