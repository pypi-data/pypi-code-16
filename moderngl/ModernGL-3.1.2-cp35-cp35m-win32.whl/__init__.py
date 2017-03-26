# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=wildcard-import
# pylint: disable=mixed-indentation

'''
	ModernGL
'''

try:
	from pylint_mock import *
except ImportError:
	pass

from .ModernGL import *

def detect_format(program, attributes):
	'''
		detect_format(program, attributes)
	'''

	return ''.join('%d%s' % (program.attributes[a].array_length * program.attributes[a].dimension, program.attributes[a].shape) for a in attributes)
