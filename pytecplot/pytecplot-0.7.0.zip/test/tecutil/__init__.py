import platform

from .test_arglist import *
from .test_index_set import *
from .test_stringlist import *
from .test_tecinterprocess import *
from .test_util import *

if platform.system() != 'Windows':
    from .test_captured_output import *
