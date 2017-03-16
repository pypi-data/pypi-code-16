import os

if os.name=='nt':
	from framework.lib import libfuncs
else:
	import sys
	sys.path.append('../..')
	from framework.lib import libfuncs
from sys import argv


def check_palindrome(var):
	var = var.strip()
	reverse_var = libfuncs.get_reverse(var)
	if var == reverse_var:
		print 'Palindrome'
	else:
		print 'Not Palindrome'

