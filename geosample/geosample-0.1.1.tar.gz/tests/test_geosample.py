#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_geosample
----------------------------------

Tests for `geosample` module.
"""

import pytest

from contextlib import contextmanager
from click.testing import CliRunner

from geosample.geosample import (
    sample_geojson,
    _random_point_in_shape,
    _sample_shape,
    _allocate_samples_to_shapes,
    _sample_shapes,
)
from geosample import cli


def test__random_point_in_shape(shape):
    result = _random_point_in_shape(shape)
    assert shape.contains(result)


def test__sample_shape(shape):
    num_samples = 100
    result = _sample_shape(shape, num_samples)
    assert len(result) == num_samples


def test__allocate_samples_to_shapes(shapes):
    result = _allocate_samples_to_shapes(shapes, 4)
    assert result == [2,2]

    result = _allocate_samples_to_shapes(shapes, 5)
    assert result == [2,3] or result == [3,2] or result == [2,2]


def test__sample_shapes(shapes):
    n = 100
    result = _sample_shapes(shapes, n)
    assert abs(len(result) - n) < 2


def test_sample_geojson(geojson):
    n = 1400
    result = sample_geojson(geojson, n)
    assert abs(len(result) - n) < 3


@pytest.mark.skip(reason='TODO')
def test__reproject_shapes(shapes):
    # http://gis.stackexchange.com/questions/166675/geopandas-shapely-what-units-it-uses-calculates-for-area-and-distance-functions
    assert False


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'geosample.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
