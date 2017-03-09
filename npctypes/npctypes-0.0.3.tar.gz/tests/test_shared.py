#!/usr/bin/env python

__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 05, 2016 9:46$"


import ctypes
import doctest
import multiprocessing
import sys
import unittest

from npctypes import shared


# Load doctests from `shared`.
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(shared))
    return tests


class TestWrappers(unittest.TestCase):
    def setUp(self):
        self.a = shared.ndarray((2, 3), float)

    def test_instance_Array(self):
        self.assertIsInstance(self.a, ctypes.Array)

    def test_Process(self):
        def test(a):
            with shared.as_ndarray(a) as nd_a:
                for i in range(nd_a.size):
                    nd_a.flat[i] = i

        p = multiprocessing.Process(
            target=test,
            args=(self.a,)
        )
        p.run()

        self.assertListEqual(list(self.a), list(range(len(self.a))))

    def test_not_writeable(self):
        with self.assertRaises(ValueError):
            with shared.as_ndarray(self.a, writeable=False) as nd_a:
                nd_a[...] = 0

    def test_not_writeable_2(self):
        with self.assertRaisesRegexp(ValueError,
                                     "assignment destination is read-only"):
            with shared.as_ndarray(self.a, writeable=False) as nd_a:
                nd_a[...] = 0

    def tearDown(self):
        del self.a


if __name__ == '__main__':
    sys.exit(unittest.main())
