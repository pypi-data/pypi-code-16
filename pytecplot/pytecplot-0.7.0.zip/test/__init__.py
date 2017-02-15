import sys

### move mock under unittest like it is in Python version 3.1+
if sys.version_info < (3,1):
    import mock
    import unittest
    sys.modules['unittest.mock'] = mock
    unittest.mock = mock

    def assertIsNone(self, obj):
        return self.assertTrue(obj is None)
    unittest.TestCase.assertIsNone = assertIsNone

    if sys.version_info < (3,3):
        def assertRegex(self, text, regexp, msg=None):
            return self.assertRegexpMatches(text, regexp, msg)
        unittest.TestCase.assertRegex = assertRegex

import argparse
import functools
import logging
import os
import platform
import random
import re
import time
import unittest

from argparse import ArgumentParser, SUPPRESS
from contextlib import contextmanager
from unittest.mock import patch, Mock

# suppress logging messages from showing up during unittests
logging.basicConfig(stream=os.devnull)

# useful for testing other platforms
#patch('platform.system', Mock(return_value='Windows')).start()

### Mock out DLL if all we are going to do is list out test cases
parser = ArgumentParser(usage=SUPPRESS)
parser.add_argument('-l', '--list',
    action='store_true',
    default=False,
    help='''just list out the test cases, but do not run them.''')
args,_ = parser.parse_known_args(sys.argv)
if args.list:
    from .mock_tecplot_module import patch_tecplot_module
    patch_tecplot_module()
    sys.modules['numpy'] = Mock()


### convenience methods for patching tecutil
def patch_tecutil(fn_name, **kwargs):
    import tecplot
    return patch.object(tecplot.tecutil._tecutil, fn_name, Mock(**kwargs))

@contextmanager
def patched_tecutil(fn_name, **kwargs):
    with patch_tecutil(fn_name, **kwargs) as p:
        yield p


# This will print out timing information for each TestCase
'''
@classmethod
def setUpClass(cls):
    cls.startTime = time.time()
@classmethod
def tearDownClass(cls):
    print("\n{}.{}: {:.3f}".format(cls.__module__, cls.__name__, time.time() - cls.startTime))
unittest.TestCase.setUpClass = setUpClass
unittest.TestCase.tearDownClass = tearDownClass
'''


def skip_on(*ex):
    """
    Unconditionally skip a test.
    """
    def decorator(test_item):
        @functools.wraps(test_item)
        def skip_wrapper(*args, **kwargs):
            try:
                test_item(*args, **kwargs)
            except ex:
                raise unittest.SkipTest(str(ex[0]))
        return skip_wrapper
    return decorator


def main():
    parser = ArgumentParser(usage=SUPPRESS)
    parser.add_argument('-r', '--random',
        action='store_true',
        default=False,
        help='''randomize ordering of test cases and further randomize
                test methods within each test case''')
    parser.add_argument('-d', '--debug',
        action='store_true',
        default=False,
        help='''Set logging output to DEBUG''')
    parser.add_argument('-l', '--list',
        action='store_true',
        default=False,
        help='''just list out the test cases, but do not run them.''')

    def print_help():
        parser._print_help()
        unittest.main()
    parser._print_help = parser.print_help
    parser.print_help = print_help

    args,unknown_args = parser.parse_known_args(sys.argv)

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    if args.list:

        def list_of_tests(tests):
            if unittest.suite._isnotsuite(tests):
                yield tests
            else:
                for test in tests._tests:
                    for t in list_of_tests(test):
                        yield t

        here = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
        tests = unittest.defaultTestLoader.discover('test',
            top_level_dir=os.path.dirname(here))

        tests = sorted(set([str(t) for t in list_of_tests(tests)]))
        tests = [str(t).replace(' (','-').replace(')','') for t in tests]

        for test in tests:
            fnname, namespace = test.split('-')
            if re.search(r'test\.examples\.', namespace):
                continue
            if platform.system() == 'Windows':
                if re.search(r'captured_output', namespace):
                    continue
            print(test)

    else:
        import tecplot as tp
        tp.session._tecinterprocess.start()

        try:
            if args.random:
                unittest.defaultTestLoader.sortTestMethodsUsing = \
                    lambda *a: random.choice((-1,1))
                def suite_init(self,tests=()):
                    self._tests = []
                    self._removed_tests = 0
                    if isinstance(tests, list):
                        random.shuffle(tests)
                    self.addTests(tests)
                unittest.defaultTestLoader.suiteClass.__init__ = suite_init

            unittest.main(argv=unknown_args)

        finally:
            tp.session.stop()
