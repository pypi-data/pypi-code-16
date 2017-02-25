__bold = '\033[1m'
__reset = '\033[0m'

class Color:
	BLACK, RED, GREEN, YELLOW, BLUE, PURPLE, TEAL, WHITE = range(30,38)

def __color_str(msg, color, bold, background=None):
	if background:
		background += 10
		if bold:
			return '\033[1;%d;%dm%s%s' % (color, background, msg, __reset)
		else:
			return '\033[%d;%dm%s%s' % (color, background, msg, __reset)
	else:
		if bold:
			return '\033[1;%dm%s%s' % (color, msg, __reset)
		else:
			return '\033[%dm%s%s' % (color, msg, __reset)

def bold(msg):
	return '%s%s%s' % (__bold, msg, __reset)

def black(msg, bold=False, background=None):
	return __color_str(msg, Color.BLACK, bold, background)

def red(msg, bold=False, background=None):
	return __color_str(msg, Color.RED, bold, background)

def green(msg, bold=False, background=None):
	return __color_str(msg, Color.GREEN, bold, background)

def yellow(msg, bold=False, background=None):
	return __color_str(msg, Color.YELLOW, bold, background)

def blue(msg, bold=False, background=None):
	return __color_str(msg, Color.BLUE, bold, background)

def purple(msg, bold=False, background=None):
	return __color_str(msg, Color.PURPLE, bold, background)

def teal(msg, bold=False, background=None):
	return __color_str(msg, Color.TEAL, bold, background)

def white(msg, bold=False, background=None):
	return __color_str(msg, Color.WHITE, bold, background)
