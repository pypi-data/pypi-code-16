# -*- coding: utf-8 -*-
# Copyright (C) 1998-2017 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Math_Func
#
# Purpose
#    Augment standard math module by additional functions
#
# Revision Dates
#     2-Mar-1998 (CT)  Creation
#    25-Aug-1998 (CT)  `intersection` optimized (use hash-table instead of
#                      iterative comparison)
#    28-Jan-1999 (CT)  `intersection` moved to `predicate.py`
#    28-Jan-1999 (MG)  `greatest_common_divisor`, `least_common_multiple`,
#                      `gcd` and `lcm` added
#    15-Feb-2001 (CT)  `gcd` streamlined
#    15-Feb-2001 (CT)  `default` added to `greatest_common_divisor` and
#                      `least_common_multiple` and check for empty `seq` added
#     4-Dec-2001 (CT)  `p2_ceil` added
#    30-Aug-2002 (CT)  `p2_ceil` corrected (division by 8 is *not* reusable)
#    27-Feb-2004 (CT)  `average` and `standard_deviation` added
#     5-Apr-2004 (CT)  `p2_ceil` changed to return a number of the same type
#                      as passed as argument instead of a real
#    10-Dec-2004 (ABR) Corrected classic int division for `lcm`
#    14-Feb-2006 (CT)  Moved into package `TFL`
#    13-Oct-2006 (PGO) `linregress` added (very simple version)
#    16-Oct-2006 (CED) `linregress` filled with life,
#                      `coefficent_of_correlation` added, functions sorted
#    17-Oct-2006 (CED) s/linregress/linear_regression/,  implement robust
#                      regression
#    17-Oct-2006 (CED) Removed `coefficent_of_correlation`,  added `residuals`
#    20-Oct-2006 (CED) s/linear_regression/linear_regression_1/, doctest added
#                      `residuals` moved out
#     7-Nov-2006 (CED) `sign` added
#    13-Dec-2006 (PGO) `periodic_pattern_gen` added
#    12-Nov-2007 (CT)  `horner` added
#    15-Jun-2010 (CT)  `periodic_pattern_gen` removed (needs to go into
#                      different module)
#    26-Feb-2016 (CT) Import `division` from `__future__`
#    19-Feb-2017 (CT) Add `median`, `median_s`
#    20-Feb-2017 (CT) Add `percentile`, `percentile_s`
#    ««revision-date»»···
#--

from   __future__  import division

from   _TFL import TFL

from   math import *
import operator

_log2 = log (2)

def average (seq) :
    """Returns the average value of the elements in `seq`.

       >>> s = (1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27)
       >>> "%4.2f" % (average (s),)
       '1.29'
    """
    return float (sum (seq)) / len (seq)
# end def average

def gcd (a, b) :
    """Calculates the greates common devisor of `a` and  `b`"""
    a = abs (a)
    b = abs (b)
    if (a < b) :
        a, b = b, a
    while (b) :
        a, b = b, a % b
    return a or 1
# end def gcd

def greatest_common_divisor (seq, default = None) :
    """Calculates the greates common devisor of `seq`"""
    result = default
    if seq :
        result = seq [0]
        for i in seq [1:] :
            result = gcd (result, i)
    return result
# end def greatest_common_divisor

def horner (x, ai) :
    """Value of polynomial `a0 + a1 * x + a2 * x**2 + ... an * x ** n` for `x`.

       >>> horner (3, (-1, 2, -6, 2))
       5
       >>> horner (-3, [8, -1, 0, 13, 4])
       -16
    """
    ia     = reversed (ai)
    result = next     (ia)
    for a in ia :
        result *= x
        result += a
    return result
# end def horner

def lcm (a, b) :
    """Calculates the least common multiple of `a` and `b`"""
    return (a // gcd (a, b)) * b
# end def lcm

def least_common_multiple (seq, default = None) :
    """Calculates the least common multiple of `seq`"""
    result = default
    if seq :
        result = seq [0]
        for i in seq [1:] :
            result = lcm (result, i)
    return result
# end def least_common_multiple

def linear_regression_1 (ys, xs) :
    """Linear regression algorithm for 2-dimensional data
       (== 1 free variable).
       (see http://en.wikipedia.org/wiki/Linear_regression)
       Returns offset and slope of a straight line approximating the
       data points given by `xs` and `ys`.

       >>> xs = [1, 2, 3]
       >>> ys = [3, 6, 9]
       >>> linear_regression_1 (ys, xs)
       (0.0, 3.0)
       >>> ys = [4, 7, 10]
       >>> linear_regression_1 (ys, xs)
       (1.0, 3.0)
    """
    assert len (xs) == len (ys)
    n       = float (len (xs))
    sx      = sum (xs)
    sy      = sum (ys)
    sxx     = sum (x * x  for x    in xs)
    sxy     = sum (x * y  for x, y in zip (xs, ys))
    k       = (n*sxy - sx*sy) / (n*sxx - sx*sx)
    d       = (sy - k*sx) / n
    return d, k
# end def linear_regression_1

def log2  (x) :
    return log (x) / _log2
# end def log2

def median (seq) :
    """Return the median value of `seq`.

    >>> median ([1, 5, 2, 8, 7])
    5
    """
    return median_s (sorted (seq))
# end def median

def median_s (sorted_seq) :
    """Return the median value of `sorted_seq`.

    >>> median ([1, 2, 2, 3, 14])
    2

    >>> median ([1, 2, 2, 3, 3, 14])
    2.5

    """
    l = len (sorted_seq)
    if l % 2 :
        result =  sorted_seq [l // 2]
    else :
        l -= 1
        result = (sorted_seq [l // 2] + sorted_seq [l // 2 + 1]) / 2.0
    return result
# end def median_s

def percentile (p, seq) :
    """Return percentile `p` of `seq`.

    >>> percentile (30, [15, 20, 35, 40, 50])
    20

    >>> percentile (40, [15, 20, 35, 40, 50])
    20

    >>> percentile (50, [15, 20, 35, 40, 50])
    35

    >>> percentile (100, [15, 20, 35, 40, 50])
    50

    """
    return percentile_s (p, sorted (seq))
# end def percentile

def percentile_s (p, sorted_seq) :
    """Return percentile `p` of `sorted_seq`.

    >>> l1 = [3, 6, 7, 8, 8,    10, 13, 15, 16, 20]
    >>> l2 = [3, 6, 7, 8, 8, 9, 10, 13, 15, 16, 20]
    >>> for l in (l1, l2) :
    ...   for p in (0, 25, 50, 75, 100) :
    ...     print ("%3s percentile of %s elements: %2s" % (p, len (l), percentile (p, l)))
      0 percentile of 10 elements:  3
     25 percentile of 10 elements:  7
     50 percentile of 10 elements:  8
     75 percentile of 10 elements: 15
    100 percentile of 10 elements: 20
      0 percentile of 11 elements:  3
     25 percentile of 11 elements:  7
     50 percentile of 11 elements:  9
     75 percentile of 11 elements: 15
    100 percentile of 11 elements: 20

    """
    l      = len (sorted_seq)
    i      = int (0.99 + (p * l) / 100) - 1 if p else 0
    result = sorted_seq [i]
    return result
# end def percentile_s

def p2_ceil (n) :
    """Return next larger power of 2 for `n`.

       >>> [p2_ceil (i) for i in range (1, 9)]
       [1, 2, 4, 4, 8, 8, 8, 8]
    """
    return n.__class__ (2 ** ceil (log2 (n)))
# end def p2_ceil

def sign (n) :
    """Returns the sign of n.

       >>> sign (4)
       1
       >>> sign (-6.9)
       -1
       >>> sign (0)
       0
    """
    if n > 0 :
        return 1
    elif n < 0 :
        return -1
    else :
        return 0
# end def sign

def standard_deviation_plain (seq) :
    """Returns the standard deviation (aka root mean square) of the elements
       in `seq`. Beware of numerical instabilities.

       >>> s = (1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27)
       >>> "%5.3f" % (standard_deviation_plain (s),)
       '0.016'
    """
    n    = len     (seq)
    mean = average (seq)
    return sqrt (sum (((mean - v) ** 2) for v in seq) / (n - 1))
# end def standard_deviation_plain

def standard_deviation (seq) :
    """Returns the standard deviation (aka root mean square) of the elements
       in `seq`. Beware numerical instabilities.

       >>> s = (1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27)
       >>> "%5.3f" % (standard_deviation (s),)
       '0.016'
    """
    n     = len (seq)
    a1    = sum (v * v for v in seq) * n
    a2    = sum (seq) ** 2
    return sqrt ((a1 - a2) / (n * (n - 1)))
# end def standard_deviation

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Math_Func
