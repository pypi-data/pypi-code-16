# coding: utf-8
from __future__ import unicode_literals

import base64
import numpy as np
import os
import platform
import sys
import unittest
import zlib

from contextlib import contextmanager
from ctypes import *
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock, PropertyMock

import tecplot as tp
from tecplot import session
from tecplot.exception import *

from test import patch_tecutil

from ..sample_data import sample_data_file

class TestInterpolate(unittest.TestCase):

    def setUp(self):
        self.filename = sample_data_file('3x3_2x2')

    def tearDown(self):
        os.remove(self.filename)

    def test_interpolate_linear(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filename)
        zouter = ds.zone('Rectangular zone outer')
        zinner = ds.zone('Rectangular zone inner')
        z = zinner.values('Z')
        self.assertTrue(np.allclose(list(z[:]), [0,0,0,0]))
        tp.data.interpolate.interpolate_linear(zinner,zouter)
        self.assertTrue(np.allclose(list(z[:]), [.5,1,1,1.5]))

    def test_failure(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filename)
        zouter = ds.zone('Rectangular zone outer')
        zinner = ds.zone('Rectangular zone inner')
        with patch_tecutil('LinearInterpolate', return_value=False):
            with self.assertRaises(TecplotSystemError):
                tp.data.interpolate.interpolate_linear(zinner,zouter)


if __name__ == '__main__':
    from .. import main
    main()
