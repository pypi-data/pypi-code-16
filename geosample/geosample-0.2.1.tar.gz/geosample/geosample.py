# -*- coding: utf-8 -*-
from __future__ import division
import random
from math import floor
from typing import List, Any #pylint: disable=unused-import
from shapely.geometry import shape, Point, MultiPoint


def _random_point_in_shape(shape): # type: (Any) -> Point
    minx, miny, maxx, maxy = shape.bounds

    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))

        if shape.contains(p):
            return p


def _sample_shape(shape, n): # type: (Any, int) -> List[Point]
    return [_random_point_in_shape(shape) for i in range(n)]


def _allocate_samples_to_shapes(shapes, n): # type: (List, int) -> List[int]
    """ Allocate total number of samples to shapes

    :param shapes:
    :param n:
    """
    areas = [s.area for s in shapes]
    total = sum(areas)
    proportions = [a/total for a in areas]

    return [int(floor(p*n)) for p in proportions]


def _sample_shapes(shapes, n, **kwargs):
    """ Generate random samples for multiple shapes

    :param shapes:
    :param n:
    :param kwargs:

    """
    samples = _allocate_samples_to_shapes(shapes, n)
    shapes_and_samples = zip(shapes, samples)
    result = [_sample_shape(s, n) for s, n in shapes_and_samples]
    flat = [item for sublist in result for item in sublist]

    return flat


def sample_geojson(features, n): # type: (Any, int) -> MultiPoint
    """ Sample geojson data

    Given a dictionary built from geojson, a list of shapely points are
    returned. The list is a sample of points from all the polygons. The sample
    size for each polygon is proportional to the polygon's area with respect to
    the total area.

    :param features: feature data in a dictionary read from geojson
    :param n: sample size

    """
    shapes = [
        shape(f['geometry']) for f in features['features']
        if f['geometry']['type'].lower() == 'polygon'
    ]

    return MultiPoint(_sample_shapes(shapes, n))
