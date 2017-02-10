# ptypes.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111

# Standard library imports
import sys
# PyPI imports
from pmisc import AE
# Intra-package imports
import pexdoc.pcontracts
import pexdoc.ptypes


###
# Test functions
###
def test_file_name_contract():
    """ Test for file_name custom contract """
    @pexdoc.pcontracts.contract(sfn='file_name')
    def func(sfn):
        """ Sample function to test file_name custom contract """
        return sfn
    items = [3, 'test\0']
    for item in items:
        AE(func, RuntimeError, 'Argument `sfn` is not valid', sfn=item)
    func('some_file.txt')
    # Test with Python executable (should be portable across systems), file
    # should be valid although not having permissions to write it
    func(sys.executable)


def test_file_name_exists_contract():
    """ Test for file_name_exists custom contract """
    @pexdoc.pcontracts.contract(sfn='file_name_exists')
    def func(sfn):
        """ Sample function to test file_name_exists custom contract """
        return sfn
    items = [3, 'test\0']
    for item in items:
        AE(func, RuntimeError, 'Argument `sfn` is not valid', sfn=item)
    exmsg = 'File _file_does_not_exist could not be found'
    AE(func, OSError, exmsg, sfn='_file_does_not_exist')
    # Test with Python executable (should be portable across systems)
    func(sys.executable)


def test_function_contract():
    """ Tests for Function pseudo-type """
    def func1():
        pass
    AE(
        pexdoc.ptypes.function,
        ValueError,
        (
            '[START CONTRACT MSG: function]Argument `*[argument_name]*` '
            'is not valid[STOP CONTRACT MSG]'
        ),
        obj='a'
    )
    items = (func1, None)
    for item in items:
        pexdoc.ptypes.function(item)


def test_non_negative_integer():
    """ Test PosInteger pseudo-type """
    items = ['b', True, -3, 5.2]
    for item in items:
        AE(
            pexdoc.ptypes.non_negative_integer,
            ValueError,
            (
                '[START CONTRACT MSG: non_negative_integer]'
                'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            ),
            obj=item
        )
    items = [0, 2]
    for item in items:
        pexdoc.ptypes.non_negative_integer(item)


def test_non_null_string():
    """ Test NonNullString pseudo-type """
    exmsg = (
        '[START CONTRACT MSG: non_null_string]'
        'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]'
    )
    items = ['', True, -3, 5.2]
    for item in items:
        AE(pexdoc.ptypes.non_null_string, ValueError, exmsg, item)
    items = ['a', 'hello']
    for item in items:
        pexdoc.ptypes.non_null_string(item)


def test_offset_range_contract():
    """ Tests for PositiveRealNumber pseudo-type """
    items = ['a', [1, 2, 3], False, -0.1, -1.1]
    for item in items:
        AE(
            pexdoc.ptypes.offset_range,
            ValueError,
            (
                '[START CONTRACT MSG: offset_range]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            ),
            obj=item
        )
    items = [0, 0.5, 1]
    for item in items:
        pexdoc.ptypes.offset_range(item)


def test_positive_real_num_contract():
    """ Tests for PositiveRealNumber pseudo-type """
    items = ['a', [1, 2, 3], False, -0.1, -2.0]
    for item in items:
        AE(
            pexdoc.ptypes.positive_real_num,
            ValueError,
            (
                '[START CONTRACT MSG: positive_real_num]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            ),
            obj=item
        )
    items = [1, 2.0]
    for item in items:
        pexdoc.ptypes.positive_real_num(item)


def test_real_num_contract():
    """ Tests for RealNumber pseudo-type """
    items = ['a', [1, 2, 3], False]
    for item in items:
        AE(
            pexdoc.ptypes.real_num,
            ValueError,
            (
                '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` '
                'is not valid[STOP CONTRACT MSG]'
            ),
            obj=item
        )
    items = [1, 2.0]
    for item in items:
        pexdoc.ptypes.real_num(item)
