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
"""
Utility methods and data types used to handle conversions and common data
handling.
"""
import math
import pyproj


_EPSG_3857 = pyproj.Proj(init='epsg:3857')
_EPSG_4326 = pyproj.Proj(init='epsg:4326')


class BaseCoordinates(object):
    """
    Base representation of the coordinates of a point using two
    axis.
    """
    def __init__(self):
        self.x = None
        self.y = None

    def __unicode__(self):
        return '{x} {y}'.format(**self.__dict__)


class LonLatCoordinates(BaseCoordinates):
    """
    Representation of the coordinates of a single point using
    latitude and longitude.
    """
    def __init__(self, lon, lat):
        self.x = float(lon)
        self.y = float(lat)

    @property
    def longitude(self):
        return self.x

    @property
    def latitude(self):
        return self.y

    def to_pixels(self, zoom):
        """
        Convert the coordinates in latitude/longitude format into
        pixel format assuming the specified level of zoom.
        """
        return _lonlat_to_pixels(self, zoom)

    def to_mercator(self):
        """
        Convert the coordinates in latitude/longitude format into
        coordinates in mercator coordinate system. (EPSG:3857)
        """
        lat = self.latitude
        lon = self.longitude
        x, y = pyproj.transform(_EPSG_4326, _EPSG_3857, lon, lat)
        return MercatorCoordinates(x, y)


class MercatorCoordinates(BaseCoordinates):
    """
    Representation of the coordinates of a single point using
    mercator coordinate system. (EPSG:3857)
    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


class PixelCoordinates(BaseCoordinates):
    """
    Representation of the coordinates of a single point on a
    map using pixels.
    """
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def to_lonlat(self, zoom):
        """
        Convert the coordinates in pixel format for the specified
        zoom level into coordinates in latitude/longitude format.
        """
        return _pixels_to_lonlat(self, zoom)


def _lonlat_to_pixels(lonlat, zoom):
    c = (128.0 / math.pi) * (2 ** zoom)
    x = c * (math.radians(lonlat.x) + math.pi)
    y = c * (math.pi - math.log(math.tan((math.pi / 4.0) + (math.radians(lonlat.y) / 2))))
    return PixelCoordinates(x, y)


def _pixels_to_lonlat(pixels, zoom):
    c = (128.0 / math.pi) * (2 ** zoom)
    x = math.degrees((pixels.x / c) - math.pi)
    y = math.degrees(2 * math.atan(math.e ** (math.pi - (pixels.y / c))) - (math.pi / 2.0))
    return LonLatCoordinates(x, y)
