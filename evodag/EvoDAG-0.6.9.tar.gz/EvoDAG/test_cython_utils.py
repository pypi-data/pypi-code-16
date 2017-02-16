# Copyright 2017 Mario Graff Guerrero

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from SparseArray import SparseArray
import numpy as np
from EvoDAG.cython_utils import fitness_SSE, fitness_SAE


def test_fitness_sse():
    fl = SparseArray.fromlist
    _ytr = [fl(np.random.uniform(-1, 1, 100)) for _ in range(4)]
    _mask = [fl(np.random.binomial(1, 0.5, 100)) for _ in range(4)]
    _hy = [fl(np.random.uniform(-1, 1, 100)) for _ in range(4)]
    f = [-ytr.SSE(hy * mask) for ytr, hy, mask in
         zip(_ytr, _hy, _mask)]
    assert np.mean(f) == fitness_SSE(_ytr, _hy, _mask)


def test_fitness_sae():
    fl = SparseArray.fromlist
    _ytr = [fl(np.random.uniform(-1, 1, 100)) for _ in range(4)]
    _mask = [fl(np.random.binomial(1, 0.5, 100)) for _ in range(4)]
    _hy = [fl(np.random.uniform(-1, 1, 100)) for _ in range(4)]
    f = [-ytr.SAE(hy * mask) for ytr, hy, mask in
         zip(_ytr, _hy, _mask)]
    assert np.mean(f) == fitness_SAE(_ytr, _hy, _mask)
    
    
