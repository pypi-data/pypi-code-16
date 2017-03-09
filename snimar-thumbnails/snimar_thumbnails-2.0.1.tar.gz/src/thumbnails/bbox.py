# -*- coding: utf-8 -*-
# =================================================================
#
# Authors: Pedro Dias <pedro.dias@ipma.pt>
#
# Copyright (c) 2016 Pedro Dias
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
from thumbnails import coordinates


class BaseBoundingBox(object):
    def __init__(self):
        self.xmin = None
        self.ymin = None
        self.xmax = None
        self.ymax = None

    def __unicode__(self):
        return '{xmin} {ymin} {xmax} {ymax}'.format(**self.__dict__)


class MercatorBoundingBox(BaseBoundingBox):
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def to_array(self):
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    @classmethod
    def new(cls, ul, lr):
        return cls(ul.x, lr.y, lr.x, ul.y)


class LonLatBoundingBox(BaseBoundingBox):
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def upper_left(self):
        return coordinates.LonLatCoordinates(self.xmin, self.ymax)

    def upper_right(self):
        return coordinates.LonLatCoordinates(self.xmax, self.ymax)

    def lower_left(self):
        return coordinates.LonLatCoordinates(self.xmin, self.ymin)

    def lower_right(self):
        return coordinates.LonLatCoordinates(self.xmax, self.ymin)

    def to_pixels(self, zoom):
        ulpx = self.upper_left().to_pixels(zoom)
        lrpx = self.lower_right().to_pixels(zoom)
        return PixelBoundingBox.new(ulpx, lrpx, zoom)

    def to_mercator(self):
        ul = self.upper_left().to_mercator()
        lr = self.lower_right().to_mercator()
        return MercatorBoundingBox.new(ul, lr)


    @classmethod
    def new(cls, ul, lr):
        return cls(ul.longitude, lr.latitude, lr.longitude, ul.latitude)


class PixelBoundingBox(BaseBoundingBox):
    def __init__(self, xmin, ymin, xmax, ymax, zoom):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.zoom = zoom

    @property
    def width(self):
        return self.xmax - self.xmin

    @property
    def height(self):
        return self.ymax - self.ymin

    @property
    def aspect_ratio(self):
        return float(self.width) / float(self.height)

    def upper_left(self):
        return coordinates.PixelCoordinates(self.xmin, self.ymin)

    def upper_right(self):
        return coordinates.PixelCoordinates(self.xmax, self.ymin)

    def lower_left(self):
        return coordinates.PixelCoordinates(self.xmin, self.ymax)

    def lower_right(self):
        return coordinates.PixelCoordinates(self.xmax, self.ymax)

    def center(self):
        return coordinates.PixelCoordinates(
            self.xmin + (self.width / 2),
            self.ymin + (self.height / 2)
        )

    def to_lonlat(self):
        ul = self.upper_left().to_lonlat(self.zoom)
        lr = self.lower_right().to_lonlat(self.zoom)
        return LonLatBoundingBox.new(ul, lr)


    @classmethod
    def new(cls, ul, lr, zoom):
        return cls(ul.x, ul.y, lr.x, lr.y, zoom)
