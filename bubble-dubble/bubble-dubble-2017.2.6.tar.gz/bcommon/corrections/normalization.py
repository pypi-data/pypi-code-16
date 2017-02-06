#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


class Normalization:
    def __init__(self):
        self._beamline = None
        self._type = 'Monitor'
        self._range = 0, 0

    @property
    def beamline(self):
        return self._beamline

    @beamline.setter
    def beamline(self, beamline):
        self._beamline = beamline

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        self._type = t

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, r):
        self._range = r

    def __call__(self, img):
        if self._type == 'Monitor':
            try:
                return {
                    'Dubble': self._dubble_monitor_normalization,
                    'SNBL': self._snbl_monitor_normalization,
                }[self._beamline](img)
            except KeyError:
                pass
        return img

    def norm_after(self, res):
        if self._type == 'Background':
            _min = np.abs(res - self._range[0]).argmin()
            _max = np.abs(res - self._range[1]).argmin()
            res[1:, :] /= res[0, _min:_max].sum()
        return res

    def _dubble_monitor_normalization(self, img):
        i1 = img.header.get('Monitor', 0)
        photo = img.header.get('Photo', 0)
        img.float()
        if i1 < 1:
            i1 = img.array.sum()
        if i1 > 1:
            img.array /= i1
            if photo:
                img.transmission = photo / i1
        return img

    def _snbl_monitor_normalization(self, img, flux=None):
        img.float()
        flux = img.header.get('Flux') or flux
        if flux:
            img.array /= flux
        return img
