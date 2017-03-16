import os
if os.name=='nt':
	from framework.lib import libfuncs
else:
	import sys
	sys.path.append('../..')
	from framework.lib import libfuncs
from sys import argv

def even_or_odd(num):
	if libfuncs.get_datatype(num)==int:
		if num%2==0 or num==0:
			print 'Even'
		else:
			print 'Odd'
			
