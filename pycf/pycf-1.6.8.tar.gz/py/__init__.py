
import sys
import pycf
import glob

__version__ = '1.6.8'

# this is to allow from pylibcf import *
__all__ = ["libCFConfig"]

# expose all symbols defined in the configuration file
from pycf.libCFConfig import *

# open the shared library when importing this module
# on Darwin the suffix is also .so!
from ctypes import CDLL
suffix = 'so'
if sys.platform == 'win32':
    suffix = 'dll'

# try opening the shared library. Depending on the python
# version the library might be called libcf.cpython-35m-...so
# keep on trying...
libs = glob.glob(pycf.__path__[0] + '/*cf*.' + suffix)
nccf = None
for lib in libs:
    try: 
        nccf = CDLL(lib)
        break
    except:
        pass
if not nccf:
    print('Unable to open libcf shared library!')

# load the netcdf library
if sys.platform != "win32":
    if sys.platform == "darwin":
        suffix = 'dylib'
    nc = CDLL(netcdf_libdir + '/libnetcdf.' + suffix)
else:
    # windows (NEED TO TEST)
    nc = CDLL(netcdf_libdir + '/netcdf.' + suffix)

