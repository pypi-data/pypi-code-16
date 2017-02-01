__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '0.2.8'
__license__ = 'Apache License, Version 2'

try:
    from .tcex import TcEx
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try app.py --lib')

from .tcex_local import TcExLocal
from .argparser import ArgParser
