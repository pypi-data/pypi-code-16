"""
Default settings for design.extras.

This module contains default values for all optional arguments in the init
function of all classes in this package.

"""
from __future__ import absolute_import, print_function, division
from builtins import *


__author__ = 'Florian Krause <florian@expyriment.org, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.9.0'
__revision__ = 'c4963ac'
__date__ = 'Thu Mar 9 13:48:59 2017 +0100'


from ... import _internals


for _plugins in [_internals.import_plugin_defaults(__file__),
                _internals.import_plugin_defaults_from_home(__file__)]:
    for _defaults in _plugins:
        exec(_defaults)
