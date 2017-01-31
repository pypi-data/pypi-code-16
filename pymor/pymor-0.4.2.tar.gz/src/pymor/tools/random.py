# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright 2013-2016 pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

from pymor.core.defaults import defaults

import numpy as np


@defaults('seed')
def new_random_state(seed=42):
    """Returns a new |NumPy| :class:`~numpy.random.RandomState`.

    Parameters
    ----------
    seed
        Seed to use for initializing the random state.

    Returns
    -------
    New `RandomState` object.
    """
    return np.random.RandomState(seed)
