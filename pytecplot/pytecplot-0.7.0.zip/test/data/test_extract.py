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
from tecplot.constant import *
from tecplot.exception import *

from test import patch_tecutil

from ..sample_data import sample_data_file

class TestExtract(unittest.TestCase):

    def setUp(self):
        self.filenames = [
            sample_data_file('10x10x10'),
            sample_data_file('3x3_2x2')]


    def tearDown(self):
        for f in self.filenames:
            os.remove(f)

    def test_interpolate_linear(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames[0])

        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian3D

        z = tp.data.extract.extract_slice(origin=(0.5,0.5,0), normal=(0,1,0),
            slicesource=SliceSource.VolumeZones, dataset=ds)
        self.assertIn(z, ds)
        self.assertEqual(z.name, 'Slc: Y=0.5')

    def test_interpolate_linear_failures(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames[0])

        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian3D

        with patch_tecutil('CreateSliceZoneFromPlneX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                tp.data.extract.extract_slice((0.5,0.5,0), (0,1,0))

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            tp.data.extract.extract_slice((0.5,0.5,100), (0,0,1))

        if __debug__:
            tp.new_layout()
            ds = tp.data.load_tecplot(self.filenames[1])

            fr = tp.active_frame()
            fr.plot_type = PlotType.Cartesian2D
            with self.assertRaises(TecplotLogicError):
                tp.data.extract.extract_slice((0.5,0.5,0), (0,1,0))

        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames[1])

        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian3D
        with self.assertRaises(TecplotLogicError):
            tp.data.extract.extract_slice((0.5,0.5,0), (0,1,0))

if __name__ == '__main__':
    from .. import main
    main()
