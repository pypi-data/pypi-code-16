# -*- coding: utf-8 -*-
# Copyright 2016-2017 Christian C. Sachs
# see LICENSE
"""
documentation
"""

from __future__ import division, unicode_literals, print_function

import numpy as np

from functools import reduce
from molyso.generic.signal import normalize, horizontal_mean, vertical_mean, each_image_slice, \
    hamming_smooth, relative_maxima

try:
    from .fast_argrelextrema import relative_extrema

    def relative_maxima(data, order=1):
        return relative_extrema(data, order=order, cmp=1)

    def relative_minima(data, order=1):
        return relative_extrema(data, order=order, cmp=-1)

except ImportError:
    relative_extrema = None
    pass


def slicewise_product_profile(image, steps, direction='horizontal', normalize_profiles=False, shift=0.0):

    mean_func = horizontal_mean if direction == 'horizontal' else vertical_mean

    def dummy(a):
        return a

    n_func = normalize if normalize_profiles else dummy

    # the next call is like 90% of all time spent on box detection ;)
    slices = [
        n_func(mean_func(image_slice)) + shift
        for n, step, image_slice in each_image_slice(image, steps, direction=direction)
        ]

    product_profile = reduce(lambda a, b: n_func(a*b), slices)

    product_profile = n_func(product_profile)

    return product_profile


def find_box(image, throw=False, subsample=1, debug=False):
    assert (type(subsample) == int)
    if subsample != 1:
        image = image[::subsample, ::subsample]

    try:
        product_profile = slicewise_product_profile(image, 20)
        product_profile = np.gradient(product_profile)

        prepared_profile = normalize(hamming_smooth(np.abs(product_profile), 3))

        pts = relative_maxima(prepared_profile, len(prepared_profile) // 4)

        l, r = sorted(zip(pts[:-1], pts[1:]), key=lambda pt: abs(0.5-(0.5*(pt[0] + pt[1]))/len(prepared_profile)))[0]

        horizontal_crop = image[:, l:r]

        # box_width = r - l

        # strip = box_width // 4

        product_profile = slicewise_product_profile(horizontal_crop, 4,
                                                    direction='vertical',
                                                    normalize_profiles=True,
                                                    shift=0.1)  # shift=0.1

        points_to_check = 8

        check_whole_image_for_vertical_crop = False

        if check_whole_image_for_vertical_crop:
            total_product_profile = slicewise_product_profile(image, 4,
                                                              direction='vertical',
                                                              normalize_profiles=True,
                                                              shift=0.1)  # shift=0.1

            with np.errstate(invalid='ignore'):
                product_profile /= total_product_profile

            _ok_values = product_profile[np.isfinite(product_profile)]

            p_min, p_max = _ok_values.min(), _ok_values.max()

            product_profile[np.isnan(product_profile)] = p_min
            product_profile[np.isinf(product_profile)] = p_max

            points_to_check = float('inf')

        pts = relative_maxima(product_profile, 10)
        spts = sorted(pts, key=lambda p: product_profile[p], reverse=True)

        pts = sorted(spts[:min(points_to_check, len(pts))])

        center_of_gravity = \
            np.sum((np.linspace(0, len(product_profile) - 1, len(product_profile)) * product_profile)) / \
            np.sum(product_profile)
        center_of_gravity /= len(product_profile)
        center_to_use = center_of_gravity if abs(center_of_gravity - 0.5) < 0.1 else 0.5

        def cost(tt, should_print=False):
            _t, _b = tt
            tf = _t / len(product_profile)
            bf = _b / len(product_profile)

            vt = product_profile[_t]
            vb = product_profile[_b]

            eccentricity = 1.0/(tf+bf)
            eccentricity_factor = 1.0 / np.exp(10.0 * (1.0-eccentricity)**2)
            length = bf - tf
            height = vt * vb
            height_delta = 1.0 - abs(vt - vb) / (0.5*(vt+vb))
            tdist = abs(tf - center_to_use)
            bdist = abs(bf - center_to_use)

            cost_value = eccentricity_factor * length * height * height_delta * tdist * bdist

            if should_print:
                def floatdict_to_str(fdict, digits=4):
                    return 'dict(' + ', '.join(('%%s=%%.%df' % (digits,)) % (k, v) for k, v in fdict.items()) + ')'

                print(
                    '%d %d %.3f\t%s' % (
                        _t, _b, cost_value, floatdict_to_str(
                            dict(
                                eccentricity=eccentricity, eccentricity_factor=eccentricity_factor,
                                length=length, height=height,
                                height_delta=height_delta, tdist=tdist, bdist=bdist
                            )
                        )
                    )
                )

            return cost_value

        # we only look at pairs of points,
        # the upper point must be upper, the lower lower
        # and the distance between them must be at least
        # 10% of the image height

        pts_generator = ((pts[_i], pts[_j])
                         for _i in range(len(pts))
                         for _j in range(_i+1, len(pts))
                         if (abs(pts[_i] - pts[_j]) / len(product_profile)) > 0.1)

        sorted_points = list(sorted(pts_generator, key=cost, reverse=True))

        if debug:
            for point in sorted_points:
                cost(point, should_print=True)

        t, b = sorted_points[0]
    except IndexError:
        if throw:
            raise RuntimeError("No box detected.")
        else:
            return 0, image.shape[0]*subsample, 0, image.shape[1]*subsample

    return t*subsample, b*subsample, l*subsample, r*subsample
