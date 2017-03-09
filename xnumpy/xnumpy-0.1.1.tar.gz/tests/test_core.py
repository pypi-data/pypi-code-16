#!/usr/bin/env python

__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 12, 2016 16:25$"


import doctest
import sys
import unittest

from xnumpy import core


# Load doctests from `types`.
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(core))
    return tests


if __name__ == '__main__':
    sys.exit(unittest.main())
