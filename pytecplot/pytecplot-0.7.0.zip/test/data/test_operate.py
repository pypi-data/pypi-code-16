# coding: utf-8
from __future__ import unicode_literals

import base64
# noinspection PyPackageRequirements
import numpy
import os
# import platform
import sys
import unittest
import zlib

from contextlib import contextmanager
from ctypes import *
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock, PropertyMock, MagicMock
from .. import patch_tecutil

import tecplot as tp
from tecplot import session
from tecplot.exception import *
from tecplot.constant import ValueLocation, FieldDataType
from tecplot.tecutil.tecinterprocess import _tecutil
from tecplot.tecutil import ArgList
from tecplot.tecutil import sv
from tecplot.data import Dataset, Variable
from tecplot.data.operate import Range

from ..sample_data import sample_data


class TestExecuteEquation(unittest.TestCase):

    def setUp(self):
        tp.new_layout()
        self.filename,self.ds = sample_data('3x3_2x2')
        self.z_inner = self.ds.zone('Rectangular zone inner')
        self.z_outer = self.ds.zone('Rectangular zone outer')
        self.z_var = self.z_inner.values('Z')  # type: Variable

    def tearDown(self):
        os.remove(self.filename)

    def test_range_option(self):
        # noinspection PyStatementEffect
        def fake_data_alter(arglist):
            for option in [sv.IMIN, sv.IMAX, sv.ISKIP,
                           sv.JMIN, sv.JMAX, sv.JSKIP,
                           sv.KMIN, sv.KMAX, sv.KSKIP]:
                with self.assertRaises(TypeError):
                    arglist[option]

            return True

        with patch_tecutil('DataAlterX', side_effect=fake_data_alter):
            # Even though we are passing Range tuples, since the
            # min/max/skip values are None, none of the corresponding
            # options should exist in the arglist value passed to
            # the fake data alter function above.
            tp.data.operate.execute_equation(
                'X', i_range=Range(None, None, None))

            tp.data.operate.execute_equation(
                'X', j_range=Range(None, None, None))

            tp.data.operate.execute_equation(
                'X', k_range=Range(None, None, None))

    def test_return_value(self):
        with patch_tecutil('DataAlterX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                tp.data.operate.execute_equation('X')

    def test_default_options(self):
        # noinspection PyStatementEffect
        def fake_data_alter(arglist):
            for option in [sv.ZONESET, sv.IMIN, sv.JMIN, sv.JSKIP,
                           sv.JMIN, sv.JMAX, sv.JSKIP,
                           sv.KMIN, sv.KMAX, sv.KSKIP,
                           sv.VALUELOCATION,
                           sv.VARDATATYPE,
                           sv.IGNOREDIVIDEBYZERO]:
                with self.assertRaises(TypeError):
                    # Accessing the option should raise a TypeError
                    # since that option should not exist in the incoming
                    # arglist.
                    arglist[option]
            return True

        with patch_tecutil('DataAlterX', side_effect=fake_data_alter):
            tp.data.operate.execute_equation('X')

    # noinspection PyUnresolvedReferences
    def test_all_execute_equation_options(self):
        equation = 'X = X + 1'
        zone_list = [self.z_inner]
        i_range = Range(2, 3, 4)
        j_range = Range(5, 6, 7)
        k_range = Range(8, 9, 10)

        value_location = ValueLocation.Nodal
        variable_data_type = FieldDataType.Byte
        ignore_divide_by_zero = True

        def fake_data_alter(arglist):
            self.assertIsInstance(arglist, ArgList)

            self.assertEqual(arglist[sv.EQUATION], equation)

            zones = [Z for Z in arglist[sv.ZONESET]]
            self.assertTrue(self.z_inner.index in zones)

            self.assertEqual(arglist[sv.IMIN], i_range.min)
            self.assertEqual(arglist[sv.IMAX], i_range.max)
            self.assertEqual(arglist[sv.ISKIP], i_range.step)
            self.assertEqual(arglist[sv.JMIN], j_range.min)
            self.assertEqual(arglist[sv.JMAX], j_range.max)
            self.assertEqual(arglist[sv.JSKIP], j_range.step)
            self.assertEqual(arglist[sv.KMIN], k_range.min)
            self.assertEqual(arglist[sv.KMAX], k_range.max)
            self.assertEqual(arglist[sv.KSKIP], k_range.step)

            self.assertEqual(arglist[sv.VALUELOCATION],
                             ValueLocation.Nodal.value)

            self.assertEqual(arglist[sv.VARDATATYPE],
                             FieldDataType.Byte.value)

            self.assertTrue(arglist[sv.IGNOREDIVIDEBYZERO])

            return True

        with patch_tecutil('DataAlterX', side_effect=fake_data_alter):
            tp.data.operate.execute_equation(
                equation,
                zones=zone_list,
                i_range=i_range,
                j_range=j_range,
                k_range=k_range,
                value_location=value_location,
                variable_data_type=variable_data_type,
                ignore_divide_by_zero=ignore_divide_by_zero)

    def test_execute_equation(self):
        self.assertTrue(numpy.allclose(list(self.z_var[:]), [0, 0, 0, 0]))
        tp.data.operate.execute_equation('{Z} = 1', zones=self.z_inner)
        self.assertTrue(numpy.allclose(list(self.z_var[:]), [1, 1, 1, 1]))

    def test_invalid_equation_parameter(self):
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                # Requires a string
                tp.data.operate.execute_equation(1+1)

            with self.assertRaises(TecplotValueError):
                # Requires non-zero length string
                tp.data.operate.execute_equation('')
        else:
            with self.assertRaises(TecplotLogicError):
                # Requires a string
                tp.data.operate.execute_equation(1+1)

            with self.assertRaises(TecplotSystemError):
                # Requires non-zero length string
                tp.data.operate.execute_equation('')

    def test_invalid_zone_set_parameter(self):
        class ClassWithoutIndexMethod(object):
            def __init__(self):
                pass  # Fake class without an .index() method

        if __debug__:
            expected_error = TecplotTypeError
        else:
            expected_error = TecplotSystemError

        with self.assertRaises(expected_error):
            tp.data.operate.execute_equation('X', zones=1)
        with self.assertRaises(expected_error):
            tp.data.operate.execute_equation('X', zones=[1])
        with self.assertRaises(TecplotTypeError):
            tp.data.operate.execute_equation(
                'X', zones=ClassWithoutIndexMethod())
        with self.assertRaises(TecplotTypeError):
            tp.data.operate.execute_equation(
                'X', zones=[ClassWithoutIndexMethod()])

    def test_zones_from_different_datasets(self):
        if __debug__:
            with self.assertRaises(TecplotValueError):
                self.z_inner.dataset.uid += 1  # Create different parent
                zone_list = [self.z_inner, self.z_outer]
                tp.data.operate.execute_equation('X = X + 1', zone_list)

    def test_range(self):
        with self.assertRaises(TypeError):
            tp.data.operate.execute_equation('X', i_range=1)
        with self.assertRaises(TypeError):
            tp.data.operate.execute_equation('X', j_range=2)
        with self.assertRaises(TypeError):
            tp.data.operate.execute_equation('X', k_range=3)

    def test_valid_location_parameter(self):
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                tp.data.operate.execute_equation('X', value_location=1)
            with self.assertRaises(TecplotTypeError):
                tp.data.operate.execute_equation(
                    'X', value_location=FieldDataType.Byte)
        else:
            with self.assertRaises(TecplotSystemError):
                tp.data.operate.execute_equation('X', value_location=1)
            with self.assertRaises(TecplotLogicError):
                tp.data.operate.execute_equation(
                    'X', value_location=FieldDataType.Byte)

    def test_variable_data_type(self):
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                tp.data.operate.execute_equation('X', variable_data_type=1)

            with self.assertRaises(TecplotTypeError):
                tp.data.operate.execute_equation(
                    'X', variable_data_type=ValueLocation.Nodal)

    def test_ignore_divide_by_zero_param_type(self):
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                tp.data.operate.execute_equation('X', ignore_divide_by_zero='Yep!')
        else:
            with self.assertRaises(TecplotLogicError):
                tp.data.operate.execute_equation('X', ignore_divide_by_zero='Yep!')

    def test_step_should_use_the_default_if_it_is_zero(self):
        # noinspection PyStatementEffect
        def fake_data_alter(arglist):
            # If skip is zero, then we should use the default
            with self.assertRaises(TypeError):
                arglist[sv.ISKIP]  # Should not exist (that is, use default)

            return True

        with patch_tecutil('DataAlterX', side_effect=fake_data_alter):
            tp.data.operate.execute_equation('X', i_range=Range(step=0))

if __name__ == '__main__':
    from .. import main
    main()
