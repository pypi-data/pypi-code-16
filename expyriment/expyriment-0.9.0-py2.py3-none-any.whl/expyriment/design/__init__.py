"""The design package.

This package provides several data structures for describing the design of an
experiment.  See also expyriment.design.extras for more design.

"""

__author__ = 'Florian Krause <florian@expyriment.org> \
              Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.9.0'
__revision__ = 'c4963ac'
__date__ = 'Thu Mar 9 13:48:59 2017 +0100'


from . import defaults
from . import permute
from . import randomize
from ._structure import Experiment, Block, Trial

from .. import _internals
_internals.active_exp = Experiment("None")

