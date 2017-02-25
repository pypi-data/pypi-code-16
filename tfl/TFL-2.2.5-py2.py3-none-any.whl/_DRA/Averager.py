# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.DRA.Averager
#
# Purpose
#    Compute average and standard deviation of data series
#
# Revision Dates
#    22-Nov-2006 (CT) Creation
#     1-Sep-2008 (CT) `moving_average` added
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#    ««revision-date»»···
#--

from   _TFL import TFL

from   _TFL.DL_List import DL_Ring

import _TFL._Meta.Object
import _TFL._DRA

import itertools
import math

class Averager (TFL.Meta.Object) :
    """Compute average and standard deviation of data series.

       >>> runner = Averager ()
       >>> runner.add (x*x for x in range (3))
       >>> "%8.2f +- %5.3f" % (runner.average, runner.standard_deviation)
       '    1.67 +- 2.082'
       >>> runner.add (2**x for x in range (3,10))
       >>> "%8.2f +- %5.3f" % (runner.average, runner.standard_deviation)
       '  102.10 +- 165.085'
    """

    average            = property (lambda s : s.sum_x / s.n)
    standard_deviation = property \
        ( lambda s : (s.n > 1) and math.sqrt
            ((s.sum_xx * s.n - s.sum_x ** 2) / (s.n * (s.n - 1))) or 0
        )

    def __init__ (self, s = []) :
        self.n      = 0
        self.sum_x  = 0.0
        self.sum_xx = 0.0
        if s :
            self.add (s)
    # end def __init__

    def add (self, s) :
        """Add elements of iterable `s`."""
        for x in s :
            self.n      += 1
            self.sum_x  += x
            self.sum_xx += x * x
    # end def add

# end class Averager

def moving_average (s, n, central = False) :
    """Generator for moving average of `n` data points over sequence `s`.

       >>> list (moving_average (range (10), 3))
       [(2, 1.0), (3, 2.0), (4, 3.0), (5, 4.0), (6, 5.0), (7, 6.0), (8, 7.0), (9, 8.0)]
       >>> list (moving_average (range (10), 4))
       [(3, 1.5), (4, 2.5), (5, 3.5), (6, 4.5), (7, 5.5), (8, 6.5), (9, 7.5)]
       >>> list (moving_average (range (10), 5))
       [(4, 2.0), (5, 3.0), (6, 4.0), (7, 5.0), (8, 6.0), (9, 7.0)]
       >>> list (moving_average (range (10), 3, True))
       [(1, 1.0), (2, 2.0), (3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0), (7, 7.0), (8, 8.0)]
       >>> list (moving_average (range (10), 5, True))
       [(2, 2.0), (3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0), (7, 7.0)]
       >>> list (moving_average (range (10), 7, True))
       [(3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0)]
       >>> list (moving_average (range (10), 9, True))
       [(4, 4.0), (5, 5.0)]
       >>> list (moving_average (range (10), 10, True))
       [(5, 4.5)]
       >>> list (moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 3, True))
       [(1, 1.2933333333333332), (2, 1.2933333333333332), (3, 1.2899999999999998), (4, 1.2966666666666664), (5, 1.293333333333333)]
       >>> list (moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 5, True))
       [(2, 1.292), (3, 1.298), (4, 1.29)]
       >>> list (moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 7, True))
       [(3, 1.2914285714285714)]
    """
    if central :
        i = n // 2
    else :
        i = n - 1
    s = iter    (s)
    w = DL_Ring (next (s) for k in range (n))
    m = float   (n)
    v = sum     (w.values ()) / m
    yield i, v
    for x in s :
        i += 1
        v += (- w.pop_front () / m) + (x / m)
        w.append (x)
        yield i, v
# end def moving_average

if __name__ != "__main__" :
    TFL.DRA._Export ("*")
### __END__ TFL.DRA.Averager
