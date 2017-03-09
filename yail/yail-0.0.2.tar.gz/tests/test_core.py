#!/usr/bin/env python

__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 20, 2016 11:43$"


import doctest
import itertools
import sys
import types
import unittest

from yail import core

from yail.core import (
    generator,
    empty,
    single,
    cycles,
    duplicate,
    split,
    indices,
    pad,
    sliding_window_filled,
    subrange,
    disperse,
)

from builtins import (
    map,
    range,
    zip,
)


# Load doctests from `types`.
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(core))
    return tests


class TestYail(unittest.TestCase):
    def setUp(self):
        pass


    def test_generator(self):
        assert list(generator(range(5))) == [0, 1, 2, 3, 4]

        assert isinstance(generator(range(5)), types.GeneratorType)
        assert issubclass(type(generator(range(5))), types.GeneratorType)
        assert type(generator(range(5))) is types.GeneratorType


    def test_empty(self):
        assert list(empty()) == []

        with self.assertRaises(StopIteration):
            next(empty())


    def test_single(self):
        assert list(single(1)) == [1]

        assert list(single(None)) == [None]

        it = single(2)
        next(it)
        with self.assertRaises(StopIteration):
            next(it)


    def test_cycles(self):
        assert list(cycles([], 5)) == []

        assert list(cycles([1], 5)) == list(itertools.repeat(1, 5))

        assert list(cycles([1, 2, 3])) == [1, 2, 3]
        assert list(cycles([1, 2, 3], 2)) == [1, 2, 3, 1, 2, 3]
        assert list(cycles([1, 2, 3], 3)) == [1, 2, 3, 1, 2, 3, 1, 2, 3]

        assert list(zip(range(9), cycles([1, 2, 3], None))) == [(0, 1),
                                                                (1, 2),
                                                                (2, 3),
                                                                (3, 1),
                                                                (4, 2),
                                                                (5, 3),
                                                                (6, 1),
                                                                (7, 2),
                                                                (8, 3)]


    def test_duplicate(self):
        assert list(duplicate([], 5)) == []

        assert list(duplicate([1], 5)) == list(itertools.repeat(1, 5))

        assert list(duplicate([1, 2, 3])) == [1, 2, 3]
        assert list(duplicate([1, 2, 3], 2)) == [1, 1, 2, 2, 3, 3]
        assert list(duplicate([1, 2, 3], 3)) == [1, 1, 1, 2, 2, 2, 3, 3, 3]


    def test_split(self):
        l = []
        assert list(map(tuple, split(0, l))) == [tuple(),
                                                 tuple(),
                                                 tuple()]

        l = [10, 20, 30, 40, 50]
        assert list(map(tuple, split(0, l))) == [tuple(),
                                                 (10,),
                                                 (20, 30, 40, 50)]

        l = [10, 20, 30, 40, 50]
        assert list(map(tuple, split(4, l))) == [(10, 20, 30, 40,),
                                                 (50,),
                                                 tuple()]

        l = [10, 20, 30, 40, 50]
        assert list(map(tuple, split(5, l))) == [(10, 20, 30, 40, 50),
                                                 tuple(),
                                                 tuple()]

        l = [10, 20, 30, 40, 50]
        assert list(map(tuple, split(2, l))) == [(10, 20),
                                                 (30,),
                                                 (40, 50)]

        l = range(10, 60, 10)
        assert list(map(tuple, split(2, l))) == [(10, 20),
                                                 (30,),
                                                 (40, 50)]

    def test_indices(self):
        assert list(indices(0)) == []
        assert list(indices(0, 2)) == []
        assert list(indices(2, 0)) == []

        assert list(indices(2, 1)) == [(0, 0), (1, 0)]
        assert list(indices(1, 2)) == [(0, 0), (0, 1)]
        assert list(indices(2, 3)) == [(0, 0),
                                       (0, 1),
                                       (0, 2),
                                       (1, 0),
                                       (1, 1),
                                       (1, 2)]


    def test_pad(self):
        assert list(pad([1,2,3])) == [1, 2, 3]
        assert list(pad([1,2,3], before=1)) == [None, 1, 2, 3]
        assert list(pad([1,2,3], after=2)) == [1, 2, 3, None, None]
        assert list(pad([1,2,3], before=1, after=2, fill=0)) == [0, 1, 2, 3,
                                                                 0, 0]
        assert list(zip(range(3), pad([1,2,3], before=None))) == [(0, None),
                                                                  (1, None),
                                                                  (2, None)]
        assert list(zip(range(6), pad([1,2,3], after=None))) == [(0, 1),
                                                                 (1, 2),
                                                                 (2, 3),
                                                                 (3, None),
                                                                 (4, None),
                                                                 (5, None)]

        padded = pad([1,2,3], before=None, after=None)
        assert list(zip(range(3), padded)) == [(0, None),
                                               (1, None),
                                               (2, None)]


    def test_sliding_window_filled(self):
        assert list(sliding_window_filled(range(5), 1)) == [(0,),
                                                            (1,),
                                                            (2,),
                                                            (3,),
                                                            (4,)]

        assert list(sliding_window_filled(range(5), 2)) == [(0, 1,),
                                                            (1, 2,),
                                                            (2, 3,),
                                                            (3, 4,)]

        assert list(sliding_window_filled(range(5), 3)) == [(0, 1, 2,),
                                                            (1, 2, 3,),
                                                            (2, 3, 4,)]

        seq = list(sliding_window_filled(range(5), 1, pad_before=True, pad_after=True))
        assert seq == [(0,),
                       (1,),
                       (2,),
                       (3,),
                       (4,)]

        seq = list(sliding_window_filled(range(5), 2, pad_before=False, pad_after=True))
        assert seq == [(0, 1,),
                       (1, 2,),
                       (2, 3,),
                       (3, 4,),
                       (4, None,)]

        seq = list(sliding_window_filled(range(5), 2, pad_before=True, pad_after=False))
        assert seq == [(None, 0,),
                       (0, 1,),
                       (1, 2,),
                       (2, 3,),
                       (3, 4,)]

        seq = list(sliding_window_filled(range(5), 2, pad_before=True, pad_after=True))
        assert seq == [(None, 0,),
                       (0, 1,),
                       (1, 2,),
                       (2, 3,),
                       (3, 4,),
                       (4, None,)]

        seq = list(sliding_window_filled(range(5), 3, pad_before=True, pad_after=True))
        assert seq == [(None, None, 0),
                       (None, 0, 1),
                       (0, 1, 2),
                       (1, 2, 3),
                       (2, 3, 4),
                       (3, 4, None),
                       (4, None, None)]


    def test_subrange(self):
        assert list(map(list, subrange(5))) == [[0], [1], [2], [3], [4]]
        assert list(map(list, subrange(0, 5))) == [[0], [1], [2], [3], [4]]
        assert list(map(list, subrange(1, 5))) == [[1], [2], [3], [4]]

        assert list(map(list, subrange(0, 10, 3))) == [[0, 1, 2],
                                                       [3, 4, 5],
                                                       [6, 7, 8],
                                                       [9]]

        assert list(map(list, subrange(0, 7, 3))) == [[0, 1, 2],
                                                      [3, 4, 5],
                                                      [6]]

        assert list(map(list, subrange(0, 7, 3, 2))) == [[0, 2],
                                                         [3, 5],
                                                         [6]]


    def test_disperse(self):
        assert list(disperse(iter(range(0)))) == []

        assert list(disperse(range(0, 0))) == []
        assert list(disperse(range(5, 5))) == []
        assert list(disperse(range(5, 0))) == []

        assert list(disperse(range(1))) == [0]
        assert list(disperse(range(2))) == [0, 1]
        assert list(disperse(range(3))) == [0, 2, 1]

        assert list(disperse(range(10))) == [0, 5, 8, 3, 9, 4, 6, 1, 7, 2]
        assert list(disperse(range(20))) == [0, 10, 15, 5, 18, 8, 13, 3,
                                             19, 9, 14, 4, 16, 6, 11, 1,
                                             17, 7, 12, 2]

        assert list(disperse(range(0, 10, 2))) == [0, 6, 8, 2, 4]


    def tearDown(self):
        pass


if __name__ == '__main__':
    sys.exit(unittest.main())
