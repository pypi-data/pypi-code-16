"""hmm.py
offline factor/variable markov oracle generation routines for vmo

Copyright (C) 2.16.2017 Cheng-i Wang

This file is part of vmo.

vmo is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

vmo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with vmo.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np


def extract_hmm_tensor(oracle, max_lsr):
    n = oracle.num_clusters()
    hmm_tensor = np.zeros((max_lsr, n, n))

    for d, l, s in zip(oracle.data[1:], oracle.lrs[1:], oracle.sfx[1:]):
        hmm_tensor[:l, d, oracle.data[s + 1]] += 1.0

    return hmm_tensor

