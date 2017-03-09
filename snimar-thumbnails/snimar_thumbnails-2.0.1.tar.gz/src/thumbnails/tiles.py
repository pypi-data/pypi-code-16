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
from thumbnails.bbox import PixelBoundingBox
from thumbnails.coordinates import PixelCoordinates
import math
import requests
import functools
import os


TILES_URL = 'http://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}'


@functools.total_ordering
class Tile(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        # Calculate the tile upper left and lower right pixel
        # coordinates and store the pixe bounding box
        ul = _tile_to_pixels(self)
        lr = PixelCoordinates(ul.x + 256.0, ul.y + 256.0)
        self.bboxpx = PixelBoundingBox.new(ul, lr, self.z)

    def to_array(self):
        return [self.x, self.y, self.z]

    def to_filename(self):
        return '{z}_{y}_{x}.jpg'.format(**self.__dict__)

    def __unicode__(self):
        return '{x} {y} {z}'.format(**self.__dict__)

    def __eq__(self, other):
        return self.z == other.z and self.x == other.x and self.y == other.y

    def __lt__(self, other):
        """
        Tiles are ordered in lexicographic format in the attribute order
        z, x, y, so that the first tile is (0, 0, 0).
        """
        if self.z < other.z:
            return True
        elif self.x < other.x:
            return True
        elif self.y < other.y:
            return True
        else:
            return False

    def to_pixels(self):
        return _tile_to_pixels(self)


def create_tile_from_pixels(pixels, zoom):
    """
    Returns a new Tile instance from the specified pixel coordinates and
    assuming the specified zoom level.
    """
    x = int(math.floor(pixels.x / 256.0))
    y = int(math.floor(pixels.y / 256.0))
    return Tile(x, y, zoom)


class TileSet(object):
    """
    Class used to manage a series of tiles.
    """
    def __init__(self, bboxpx):
        self.tiles = {}
        self.bboxpx = bboxpx
        self.tileset_bboxpx = None

    def _process(self):
        corners = [
            self.bboxpx.upper_left(),
            self.bboxpx.upper_right(),
            self.bboxpx.lower_left(),
            self.bboxpx.lower_right()
        ]

        min_tile = None
        max_tile = None

        for corner in corners:
            corner_tile = create_tile_from_pixels(corner, self.bboxpx.zoom)
            if unicode(corner_tile) not in self.tiles.keys():
                self.tiles[unicode(corner_tile)] = corner_tile

                min_tile = corner_tile if (min_tile is None) or (min_tile > corner_tile) else min_tile
                max_tile = corner_tile if (max_tile is None) or (max_tile < corner_tile) else max_tile

        ul = _tile_to_pixels(min_tile)
        lr = _tile_to_pixels(max_tile)
        lr.x += 256
        lr.y += 256

        self.tileset_bboxpx = PixelBoundingBox.new(ul, lr, self.bboxpx.zoom)

    def retrieve(self, storage):
        self._process()
        destinations = []

        for tile in self.tiles.values():
            url = TILES_URL.format(x=tile.x, y=tile.y, z=tile.z)
            response = requests.get(url)
            destination = os.path.join(storage, tile.to_filename())
            with open(destination, 'wb') as fp:
                for chunk in response:
                    fp.write(chunk)
            destinations.append(destination)

        return destinations


def _tile_to_pixels(tile):
    return PixelCoordinates(tile.x * 256.0, tile.y * 256.0)
