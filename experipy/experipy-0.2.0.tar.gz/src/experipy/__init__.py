from __future__ import absolute_import

from . import (
    exp,
    grammar,
    system,
    utils,
)


__version__     = "0.2.0"

__title__       = "experipy"
__description__ = "A framework for writing and running Computational Science experiments"
__uri__         = "https://github.com/Elemnir/experipy"

__author__      = "Adam Howard"
__email__       = "ahoward0920@gmail.com"

__license__     = "BSD 3-clause"
__copyright__   = "Copyright (c) 2016 Adam Howard"


Experiment  = exp.Experiment
Namespace   = utils.Namespace

__all__ = [
    "exp",
    "grammar",
    "system",
    "utils",
    "Experiment",
    "Namespace",
]
