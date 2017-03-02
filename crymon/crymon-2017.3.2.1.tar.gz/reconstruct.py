#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import numpy as np
from cryio import cbfimage
from . import _crymon


LAYER_3D = 0
LAYER_2D = 1


class HKL(ctypes.Structure):
    _fields_ = [
        ('h', ctypes.c_float),
        ('k', ctypes.c_float),
        ('l', ctypes.c_float),
    ]


class Slice(ctypes.Structure):
    _fields_ = [
        ('p0', HKL),
        ('p1', HKL),
        ('pc', HKL),
        ('thickness', ctypes.c_float),
        ('qmax', ctypes.c_float),
        ('dQ', ctypes.c_float),
        ('downsample', ctypes.c_uint32),
        ('x', ctypes.c_uint32),
        ('y', ctypes.c_uint32),
        ('z', ctypes.c_uint32),
        ('lorentz', ctypes.c_uint32),
        ('scale', ctypes.c_uint32),
    ]


class Volume(_crymon._ccp4_encode):
    def __init__(self, par, s):
        super().__init__(par, s, LAYER_3D)

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(bytes(self))


class Layer(_crymon._ccp4_encode):
    def __init__(self, par, s):
        super().__init__(par, s, LAYER_2D)

    def save(self, filepath):
        cbf = cbfimage.CbfImage()
        cbf.array = np.asarray(self, np.int32)
        cbf.save_cbf(filepath)
