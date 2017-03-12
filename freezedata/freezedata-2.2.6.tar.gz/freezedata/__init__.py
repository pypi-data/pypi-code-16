import os
from .freezedata import freeze_data

DIR = os.path.dirname(__file__)
README = os.path.join(DIR, 'README.rst')

__doc__ = open(README).read()

del os, DIR, README
del freezedata
