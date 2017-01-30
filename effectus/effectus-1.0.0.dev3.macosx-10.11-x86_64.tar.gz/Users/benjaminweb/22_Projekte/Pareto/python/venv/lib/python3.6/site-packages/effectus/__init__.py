"""
    effectus
    ~~~~~~~~

    effectus tells you which minority of causes provokes which
    majority of effects. You provide it with a series of numbers.
    It tells you whether a pareto distribution is present.

    :copyright: (c) 2017 by Benjamin Weber
    :license: MIT, see LICENSE for more details.
"""

from .core import (make_summary, attain_effects, attain_causes,
                   separate_causes, separate_effects)

from .pareto import control_limit, entropy, ratio, pareto

from .helpers import (reduce_values, write_reduced_values,
                      unfold_values)

__all__ = [
    # core
    'make_summary', 'attain_effects', 'attain_causes',
    'separate_causes', 'separate_effects',

    # helpers
    'reduce_values', 'write_reduced_values', 'unfold_values',

    # pareto
    'control_limit', 'entropy', 'ratio', 'pareto',
]

__version__ = '1.0.0-dev3'
VERSION = __version__
