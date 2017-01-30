# Copyright 2016 Mario Graff Guerrero

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
from nose.tools import assert_almost_equals
from random import random


def random_lst(size=100, p=0.5):
    lst = []
    for i in range(size):
        if random() < p:
            lst.append(random())
        else:
            lst.append(0)
    return lst


def test_sum():
    for p in [0.5]:
        a = random_lst(size=100000, p=p)
        b = random_lst(size=100000, p=p)
        a[10] = 12.433
        b[10] = -12.433
        for i in range(100):
            c = SparseArray.fromlist(a) + SparseArray.fromlist(b)
            # c = SparseArray.fromlist(a).sin()

test_sum()
