# -*- coding: utf-8 -*-

"""
referencepytest.py: pytest interface to tdda reference testing.

Source repository: http://github.com/tdda/tdda

License: MIT

Copyright (c) Stochastic Solutions Limited 2016


This provides all of the methods in the ReferenceTest class, but as
module functions rather than class methods, using python's native
'assert' mechanism as its means of making assertions.

For example:

    from tdda.referencetest import referencepytest
    import my_module

    def test_my_table_function(ref):
        result = my_module.my_function()
        ref.assertStringCorrect(result, 'result.txt', kind='table')

    def test_my_graph_function(ref):
        result = my_module.my_function()
        ref.assertStringCorrect(result, 'result.txt', kind='graph')

with a conftest.py containing:

    import pytest
    from tdda.referencetest import referencepytest

    def pytest_addoption(parser):
        referencepytest.addoption(parser)

    @pytest.fixture(scope='module')
    def ref(request):
        r = referencepytest.ref(request)
        r.set_data_location('/data')
        return r

Run with the --write-all option to regenerate the reference data. If the
-s option is also provided (to disable pytest output capturing), it will
report the names of the files it has regenerated.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sys

import pytest

from tdda.referencetest.referencetest import ReferenceTest


def pytest_assert(x, msg):
    """
    assertion using standard python assert statement, as expected by pytest.
    """
    assert x, msg


def ref(request):
    """
    Support for dependency injection via a pytest fixture.

    A test's conftest.py should define a fixture function for injecting
    a ReferenceTest instance, which should just call this function.
    """
    if request.config.getoption('--wquiet'):
        ReferenceTest.set_default(verbose=False)
    if request.config.getoption('--write-all'):
        ReferenceTest.set_regeneration()
    else:
        regen = request.config.getoption('--write')
        if regen:
            for r in regen:
                for kind in r.split(','):
                    ReferenceTest.set_regeneration(kind)
    return ReferenceTest(pytest_assert)


def addoption(parser):
    """
    Support for the --write and --write-all command-line options.

    A test's conftest.py should declare extra options by defining a
    pytest_addoption function which should just call this.

    It extends pytest to include --write and --write-all option flags
    which can be used to control regeneration of reference results.

    To regenerate all reference results:
        pytest -s --write-all

    To regenerate just a particular kind of reference (e.g. table results):
        pytest -s --write tables

    To regenerate a number of different kinds of reference (e.g. both table
    and graph results):
        pytest -s --write tables graphs

    Note that it reports on each file it regenerates, unless the --wquiet
    option is set; but unless you run pytest with the -s option, this
    reporting will be eaten up by pytest as part of its standard 'capturing'.
    """
    parser.addoption('--write', action='store', nargs='+', default=None,
                     help='--write: rewrite named reference results kinds')
    parser.addoption('--write-all', action='store_true',
                     help='--write-all: rewrite all reference results')
    parser.addoption('--wquiet', action='store_true',
                     help='--wquiet: when rewriting results, do so quietly')

