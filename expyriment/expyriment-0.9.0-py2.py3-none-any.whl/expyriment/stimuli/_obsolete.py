#!/usr/bin/env python

"""
Obsolete stimuli

Calls are merely defined to give user appropriate error feedback

"""
from __future__ import absolute_import, print_function, division
from builtins import *

__author__ = 'Florian Krause <florian@expyriment.org>, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.9.0'
__revision__ = 'c4963ac'
__date__ = 'Thu Mar 9 13:48:59 2017 +0100'

class Dot(object):
    """OBSOLETE CLASS: Please use Circle!"""

    def __init__(self, radius=None, colour=None, position=None):
        """OBSOLETE CLASS: Please use Circle!

        """

        raise DeprecationWarning("Dot is an obsolete class. Please use Circle!")


class Frame(object):
    """OBSOLETE CLASS: Please use Rectangle!"""

    def __init__(self, size=None, position=None, frame_line_width=None,
                 colour=None, anti_aliasing=None, line_width=None):
        """OBSOLETE CLASS: Please use Rectangle with a line_width > 0!

        """
        raise DeprecationWarning("Frame is an obsolete class. Please use Rectangle with a line_width > 0!")