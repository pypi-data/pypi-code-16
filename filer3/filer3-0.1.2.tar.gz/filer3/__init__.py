import pkg_resources

from filer3.filer3 import Filer

__version__ = pkg_resources.get_distribution('filer3').version

Filer = Filer