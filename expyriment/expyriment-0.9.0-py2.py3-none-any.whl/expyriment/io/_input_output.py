"""
The base module of io.

This module contains the base classes for input and output.

All classes in this module should be called directly via expyriment.io.*.

"""

from __future__ import absolute_import, print_function, division

__author__ = 'Florian Krause <florian@expyriment.org>, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.9.0'
__revision__ = 'c4963ac'
__date__ = 'Thu Mar 9 13:48:59 2017 +0100'


from . import defaults
from .._internals import Expyriment_object


class Input(Expyriment_object):
    """A class implementing a general input."""

    def __init__(self):
        """Create an input."""
        Expyriment_object.__init__(self)


class Output(Expyriment_object):
    """A class implementing a general output."""

    def __init__(self):
        """Create an output."""
        Expyriment_object.__init__(self)
