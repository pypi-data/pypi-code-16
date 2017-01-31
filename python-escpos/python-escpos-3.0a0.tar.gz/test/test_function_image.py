#!/usr/bin/env python
""" Image function tests- Check that image print commands are sent correctly.

:author: `Michael Billington <michael.billington@gmail.com>`_
:organization: `python-escpos <https://github.com/python-escpos>`_
:copyright: Copyright (c) 2016 `Michael Billington <michael.billington@gmail.com>`_
:license: MIT
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import escpos.printer as printer
from PIL import Image


# Raster format print
def test_bit_image_black():
    """
    Test printing solid black bit image (raster)
    """
    instance = printer.Dummy()
    instance.image('test/resources/canvas_black.png', impl="bitImageRaster")
    assert(instance.output == b'\x1dv0\x00\x01\x00\x01\x00\x80')
    # Same thing w/ object created on the fly, rather than a filename
    instance = printer.Dummy()
    im = Image.new("RGB", (1, 1), (0, 0, 0))
    instance.image(im, impl="bitImageRaster")
    assert(instance.output == b'\x1dv0\x00\x01\x00\x01\x00\x80')


def test_bit_image_white():
    """
    Test printing solid white bit image (raster)
    """
    instance = printer.Dummy()
    instance.image('test/resources/canvas_white.png', impl="bitImageRaster")
    assert(instance.output == b'\x1dv0\x00\x01\x00\x01\x00\x00')


def test_bit_image_both():
    """
    Test printing black/white bit image (raster)
    """
    instance = printer.Dummy()
    instance.image('test/resources/black_white.png', impl="bitImageRaster")
    assert(instance.output == b'\x1dv0\x00\x01\x00\x02\x00\xc0\x00')


def test_bit_image_transparent():
    """
    Test printing black/transparent bit image (raster)
    """
    instance = printer.Dummy()
    instance.image('test/resources/black_transparent.png', impl="bitImageRaster")
    assert(instance.output == b'\x1dv0\x00\x01\x00\x02\x00\xc0\x00')


# Column format print
def test_bit_image_colfmt_black():
    """
    Test printing solid black bit image (column format)
    """
    instance = printer.Dummy()
    instance.image('test/resources/canvas_black.png', impl="bitImageColumn")
    assert(instance.output == b'\x1b3\x10\x1b*!\x01\x00\x80\x00\x00\x0a\x1b2')


def test_bit_image_colfmt_white():
    """
    Test printing solid white bit image (column format)
    """
    instance = printer.Dummy()
    instance.image('test/resources/canvas_white.png', impl="bitImageColumn")
    assert(instance.output == b'\x1b3\x10\x1b*!\x01\x00\x00\x00\x00\x0a\x1b2')


def test_bit_image_colfmt_both():
    """
    Test printing black/white bit image (column format)
    """
    instance = printer.Dummy()
    instance.image('test/resources/black_white.png', impl="bitImageColumn")
    assert(instance.output == b'\x1b3\x10\x1b*!\x02\x00\x80\x00\x00\x80\x00\x00\x0a\x1b2')


def test_bit_image_colfmt_transparent():
    """
    Test printing black/transparent bit image (column format)
    """
    instance = printer.Dummy()
    instance.image('test/resources/black_transparent.png', impl="bitImageColumn")
    assert(instance.output == b'\x1b3\x10\x1b*!\x02\x00\x80\x00\x00\x80\x00\x00\x0a\x1b2')


# Graphics print
def test_graphics_black():
    """
    Test printing solid black graphics
    """
    instance = printer.Dummy()
    instance.image('test/resources/canvas_black.png', impl="graphics")
    assert(instance.output == b'\x1d(L\x0b\x000p0\x01\x011\x01\x00\x01\x00\x80\x1d(L\x02\x0002')


def test_graphics_white():
    """
    Test printing solid white graphics
    """
    instance = printer.Dummy()
    instance.image('test/resources/canvas_white.png', impl="graphics")
    assert(instance.output == b'\x1d(L\x0b\x000p0\x01\x011\x01\x00\x01\x00\x00\x1d(L\x02\x0002')


def test_graphics_both():
    """
    Test printing black/white graphics
    """
    instance = printer.Dummy()
    instance.image('test/resources/black_white.png', impl="graphics")
    assert(instance.output == b'\x1d(L\x0c\x000p0\x01\x011\x02\x00\x02\x00\xc0\x00\x1d(L\x02\x0002')


def test_graphics_transparent():
    """
    Test printing black/transparent graphics
    """
    instance = printer.Dummy()
    instance.image('test/resources/black_transparent.png', impl="graphics")
    assert(instance.output == b'\x1d(L\x0c\x000p0\x01\x011\x02\x00\x02\x00\xc0\x00\x1d(L\x02\x0002')


def test_large_graphics():
    """
    Test whether 'large' graphics that induce a fragmentation are handled correctly.
    """
    instance = printer.Dummy()
    instance.image('test/resources/black_white.png', impl="bitImageRaster", fragment_height=1)
    assert(instance.output == b'\x1dv0\x00\x01\x00\x01\x00\xc0\x1dv0\x00\x01\x00\x01\x00\x00')
