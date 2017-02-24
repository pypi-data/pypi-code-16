# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package CAL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    CAL.Range_DT
#
# Purpose
#    Represent a range of values of some datetime element type
#
# Revision Dates
#    26-Jun-2016 (CT) Creation
#     9-Sep-2016 (CT) Add `FO`
#    11-Oct-2016 (CT) Move from `TFL` to `CAL`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                       import CAL

from   _CAL.Date                  import Date
from   _CAL.Delta                 import Date_Delta, Time_Delta
from   _CAL.Time                  import Time

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _TFL.portable_repr         import portable_repr

import _TFL._Meta.Object
import _TFL._Meta.Once_Property

import _TFL.Range

import datetime
import operator

class _M_Range_DT_ (TFL._Range_Discrete_.__class__) :
    """Meta class for `_Range_DT_`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if cls.S_Type is not None and not cls.finite :
            cls.finite = dict (lower = cls.S_Type.min, upper = cls.S_Type.max)
    # end def __init__

# end class _M_Range_DT_

class _Range_DT_ \
        (TFL.Meta.BaM (TFL._Range_Discrete_, metaclass = _M_Range_DT_)) :
    """Base class for ranges of datetime-based values."""

    @property
    def duration (self) :
        """Duration of temporal range."""
        return self.length
    # end def duration

    @property
    def finish (self) :
        """Value of upper bound of temporal range."""
        return self.upper
    # end def finish

    @property
    def start (self) :
        """Value of lower bound of temporal range."""
        return self.lower
    # end def start

    @classmethod
    def _sub_type_from_str (cls, s) :
        return cls.C_Type.from_string (s)._body
    # end def _sub_type_from_str

# end class _Range_DT_

class Date_Range (_Range_DT_) :
    """Range of date values."""

    C_Type     = Date
    D_Type     = Date_Delta
    S_Type     = datetime.date

    delta      = Date_Delta (days = 1)
    """Default delta between adjacent values of `Date_Range` is one day."""

    def _length (self, lower, upper) :
        return ((upper - lower).days // self.delta.days) + 1
    # end def _length

    def _sub_type_add (self, v, delta) :
        if not isinstance (delta, (self.D_Type, self.D_Type._Type)) :
            delta = self.delta * delta
        return v + delta
    # end def _sub_type_add

    def _sub_type_sub (self, v, delta) :
        if not isinstance (delta, (self.D_Type, self.D_Type._Type)) :
            delta = self.delta * delta
        return v - delta
    # end def _sub_type_sub

# end class Date_Range

class Time_Range (_Range_DT_) :
    """Range of time values."""

    C_Type     = Time
    D_Type     = Time_Delta
    S_Type     = datetime.time

    delta      = Time_Delta (microseconds = 1)
    """Default delta between adjacent values of `Time_Range` is one microsecond.

       Unlike descendent classes redefining `delta`, this makes `Time_Range` a
       funny mixture of continuous and discrete.
    """

    def _length (self, lower, upper) :
        u_l = (self.C_Type (time = upper) - self.C_Type (time = lower))
        return int (round ((float (u_l) / float (self.delta)))) + 1
    # end def _length

    def _sub_type_add (self, v, delta) :
        if not isinstance (delta, (self.D_Type, self.D_Type._Type)) :
            delta = self.delta * delta
        result = self.C_Type (time = v) + delta
        return result._body
    # end def _sub_type_add

    def _sub_type_as_str (self, v) :
        result = "%s" % (v, )
        if result.endswith (":00") :
            result = result [:-3]
        return result
    # end def _sub_type_as_str

    def _sub_type_sub (self, v, delta) :
        if not isinstance (delta, self.D_Type) :
            delta = self.delta * delta
        result = self.C_Type (time = v) - delta
        return result._body
    # end def _sub_type_sub

# end class Time_Range

class Time_Range_H (Time_Range) :
    """Range of time values with 1-hour delta."""

    delta      = Time_Delta (hours = 1)
    """Default delta between adjacent values of `Time_Range_H` is one hour."""

# end class Time_Range_H

class Time_Range_M (Time_Range) :
    """Range of time values with 1-minute delta."""

    delta      = Time_Delta (minutes = 1)
    """Default delta between adjacent values of `Time_Range_M` is one minute."""

# end class Time_Range_M

class Time_Range_15m (Time_Range) :
    """Range of time values with 15-minute delta."""

    delta      = Time_Delta (minutes = 15)
    """Default delta between adjacent values of `Time_Range_15m` is 15 minutes."""

# end class Time_Range_15m

class Time_Range_30m (Time_Range) :
    """Range of time values with 30-minute delta."""

    delta      = Time_Delta (minutes = 30)
    """Default delta between adjacent values of `Time_Range_30m` is 30 minutes."""

# end class Time_Range_30m

_test_date_range = r"""
    >>> from _TFL.Range import _show_ab, _show_adj, _show_fs, _show_intersection, _show_ovl, _show_sb, _show_union

    >>> R   = Date_Range
    >>> dtd = R.S_Type

    >>> dd1 = R.delta
    >>> d1  = dtd (2016, 6, 1)
    >>> d2  = d1 + dd1
    >>> d3  = d2 + dd1
    >>> d4  = d3 + dd1
    >>> d5  = d4 + dd1
    >>> d6  = d5 + dd1

    >>> infinite = R ()
    >>> infinite_l = R (None, d2)
    >>> infinite_u = R (d2, None)
    >>> infinite
    Date_Range (None, None, '[)')
    >>> print (infinite, infinite_l, infinite_u)
    [None, None) [None, 2016-06-02) [2016-06-02, None)
    >>> bool (infinite), bool (infinite_l), bool (infinite_u)
    (True, True, True)
    >>> infinite in infinite, infinite_l in infinite, infinite_u in infinite
    (True, True, True)
    >>> infinite in infinite_l, infinite in infinite_u, infinite_l in infinite_u
    (False, False, False)
    >>> print (portable_repr ((infinite.duration, infinite_l.duration, infinite_u.duration)))
    (3652058, 736116, 2915942)

    >>> empty = R (d2, d2)
    >>> empty
    Date_Range (datetime.date(2016, 6, 2), datetime.date(2016, 6, 2), '[)')
    >>> print (empty)
    [2016-06-02, 2016-06-02)
    >>> bool (empty), empty.is_empty
    (False, True)
    >>> empty.LB.bound, empty.LB.first, empty.LB.inf
    (datetime.date(2016, 6, 2), datetime.date(2016, 6, 2), datetime.date(1, 1, 1))
    >>> empty.UB.bound, empty.UB.first, empty.UB.inf
    (datetime.date(2016, 6, 2), datetime.date(2016, 6, 1), datetime.date(9999, 12, 31))
    >>> empty in infinite, empty in infinite_l, empty in infinite_u
    (False, False, False)
    >>> empty.duration
    0

    >>> point = R (empty.lower, empty.upper, "[]")
    >>> point
    Date_Range (datetime.date(2016, 6, 2), datetime.date(2016, 6, 2), '[]')
    >>> print (point)
    [2016-06-02, 2016-06-02]
    >>> bool (point)
    True
    >>> point.LB.bound, point.LB.first, point.LB.inf
    (datetime.date(2016, 6, 2), datetime.date(2016, 6, 2), datetime.date(1, 1, 1))
    >>> point.UB.bound, point.UB.first, point.UB.inf
    (datetime.date(2016, 6, 2), datetime.date(2016, 6, 2), datetime.date(9999, 12, 31))
    >>> point in infinite, point in infinite_l, point in infinite_u
    (True, False, True)
    >>> point.duration
    1

    >>> point_x = R (point.lower, point.lower + dd1, "[)")
    >>> point_x
    Date_Range (datetime.date(2016, 6, 2), datetime.date(2016, 6, 3), '[)')
    >>> print (point_x)
    [2016-06-02, 2016-06-03)
    >>> bool (point_x)
    True
    >>> point_x.LB.bound, point_x.LB.first, point_x.LB.inf
    (datetime.date(2016, 6, 2), datetime.date(2016, 6, 2), datetime.date(1, 1, 1))
    >>> point_x.UB.bound, point_x.UB.first, point_x.UB.inf
    (datetime.date(2016, 6, 3), datetime.date(2016, 6, 2), datetime.date(9999, 12, 31))
    >>> point_x in infinite, point_x in infinite_l, point_x in infinite_u
    (True, False, True)
    >>> point_x.duration
    1

    >>> ii_24 = R (d2, d4, "[]")
    >>> ix_24 = R (d2, d4, "[)")
    >>> xi_24 = R (d2, d4, "(]")
    >>> xx_24 = R (d2, d4, "()")
    >>> ii_25 = R (d2, d5, "[]")
    >>> ix_25 = R (d2, d5, "[)")
    >>> xi_25 = R (d2, d5, "(]")
    >>> xx_25 = R (d2, d5, "()")

    >>> for r in (point, point_x, ii_24) :
    ...     print (r.FO, r.FO.lower, r.FO.upper)
    [2016-06-02, 2016-06-02] 2016-06-02 2016-06-02
    [2016-06-02, 2016-06-03) 2016-06-02 2016-06-03
    [2016-06-02, 2016-06-04] 2016-06-02 2016-06-04

    >>> for r in (point, point_x, ii_24) :
    ...     print (r.FO, r.FO.lower, r.FO.upper)
    [2016-06-02, 2016-06-02] 2016-06-02 2016-06-02
    [2016-06-02, 2016-06-03) 2016-06-02 2016-06-03
    [2016-06-02, 2016-06-04] 2016-06-02 2016-06-04

    >>> for r in (ii_24, ix_24, xi_24, xx_24) :
    ...     print (r, r.duration, tuple (r))
    [2016-06-02, 2016-06-04] 3 (datetime.date(2016, 6, 2), datetime.date(2016, 6, 3), datetime.date(2016, 6, 4))
    [2016-06-02, 2016-06-04) 2 (datetime.date(2016, 6, 2), datetime.date(2016, 6, 3))
    (2016-06-02, 2016-06-04] 2 (datetime.date(2016, 6, 3), datetime.date(2016, 6, 4))
    (2016-06-02, 2016-06-04) 1 (datetime.date(2016, 6, 3),)

    >>> for r in (ii_24, ix_24, xi_24, xx_24) :
    ...     print (r, portable_repr (r.range_pattern.match (pyk.text_type (r)).groupdict ()))
    [2016-06-02, 2016-06-04] {'LB' : '[', 'UB' : ']', 'lower' : '2016-06-02', 'upper' : '2016-06-04'}
    [2016-06-02, 2016-06-04) {'LB' : '[', 'UB' : ')', 'lower' : '2016-06-02', 'upper' : '2016-06-04'}
    (2016-06-02, 2016-06-04] {'LB' : '(', 'UB' : ']', 'lower' : '2016-06-02', 'upper' : '2016-06-04'}
    (2016-06-02, 2016-06-04) {'LB' : '(', 'UB' : ')', 'lower' : '2016-06-02', 'upper' : '2016-06-04'}

    >>> for i in range (2, 5) :
    ...     v = dtd (2016, 6, i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (v, "in", r, ":", v in r)
    2016-06-02 in [2016-06-02, 2016-06-04] : True
    2016-06-02 in [2016-06-02, 2016-06-04) : True
    2016-06-02 in (2016-06-02, 2016-06-04] : False
    2016-06-02 in (2016-06-02, 2016-06-04) : False
    2016-06-03 in [2016-06-02, 2016-06-04] : True
    2016-06-03 in [2016-06-02, 2016-06-04) : True
    2016-06-03 in (2016-06-02, 2016-06-04] : True
    2016-06-03 in (2016-06-02, 2016-06-04) : True
    2016-06-04 in [2016-06-02, 2016-06-04] : True
    2016-06-04 in [2016-06-02, 2016-06-04) : False
    2016-06-04 in (2016-06-02, 2016-06-04] : True
    2016-06-04 in (2016-06-02, 2016-06-04) : False

    >>> for i in range (2, 5) :
    ...     v = R.D_Type (days = i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r, "+", v, ":", r + v, "" if v+r == r+v else "*** + isn't communitative ***")
    [2016-06-02, 2016-06-04] + 2 days, 0:00:00 : [2016-06-04, 2016-06-06]
    [2016-06-02, 2016-06-04) + 2 days, 0:00:00 : [2016-06-04, 2016-06-06)
    (2016-06-02, 2016-06-04] + 2 days, 0:00:00 : (2016-06-04, 2016-06-06]
    (2016-06-02, 2016-06-04) + 2 days, 0:00:00 : (2016-06-04, 2016-06-06)
    [2016-06-02, 2016-06-04] + 3 days, 0:00:00 : [2016-06-05, 2016-06-07]
    [2016-06-02, 2016-06-04) + 3 days, 0:00:00 : [2016-06-05, 2016-06-07)
    (2016-06-02, 2016-06-04] + 3 days, 0:00:00 : (2016-06-05, 2016-06-07]
    (2016-06-02, 2016-06-04) + 3 days, 0:00:00 : (2016-06-05, 2016-06-07)
    [2016-06-02, 2016-06-04] + 4 days, 0:00:00 : [2016-06-06, 2016-06-08]
    [2016-06-02, 2016-06-04) + 4 days, 0:00:00 : [2016-06-06, 2016-06-08)
    (2016-06-02, 2016-06-04] + 4 days, 0:00:00 : (2016-06-06, 2016-06-08]
    (2016-06-02, 2016-06-04) + 4 days, 0:00:00 : (2016-06-06, 2016-06-08)

    >>> for i in range (2, 5) :
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r, "-", i, ":", r - i)
    [2016-06-02, 2016-06-04] - 2 : [2016-05-31, 2016-06-02]
    [2016-06-02, 2016-06-04) - 2 : [2016-05-31, 2016-06-02)
    (2016-06-02, 2016-06-04] - 2 : (2016-05-31, 2016-06-02]
    (2016-06-02, 2016-06-04) - 2 : (2016-05-31, 2016-06-02)
    [2016-06-02, 2016-06-04] - 3 : [2016-05-30, 2016-06-01]
    [2016-06-02, 2016-06-04) - 3 : [2016-05-30, 2016-06-01)
    (2016-06-02, 2016-06-04] - 3 : (2016-05-30, 2016-06-01]
    (2016-06-02, 2016-06-04) - 3 : (2016-05-30, 2016-06-01)
    [2016-06-02, 2016-06-04] - 4 : [2016-05-29, 2016-05-31]
    [2016-06-02, 2016-06-04) - 4 : [2016-05-29, 2016-05-31)
    (2016-06-02, 2016-06-04] - 4 : (2016-05-29, 2016-05-31]
    (2016-06-02, 2016-06-04) - 4 : (2016-05-29, 2016-05-31)

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-04] : True True
    [2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-04) : False False
    [2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-04] : False False
    [2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-04) : False False
    [2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-04] : False False
    [2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-04) : True True
    [2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-04] : False False
    [2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-04) : False False
    (2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-04] : False False
    (2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-04) : False False
    (2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-04] : True True
    (2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-04) : False False
    (2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-04] : False False
    (2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-04) : False False
    (2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-04] : False False
    (2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-04) : True True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-05] : False False
    [2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-05) : True True
    [2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-05] : False False
    [2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-05) : False False
    [2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-05] : False False
    [2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-05) : False False
    [2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-05] : False False
    [2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-05) : False False
    (2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-05] : False False
    (2016-06-02, 2016-06-04] == [2016-06-02, 2016-06-05) : False False
    (2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-05] : False False
    (2016-06-02, 2016-06-04] == (2016-06-02, 2016-06-05) : True True
    (2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-05] : False False
    (2016-06-02, 2016-06-04) == [2016-06-02, 2016-06-05) : False False
    (2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-05] : False False
    (2016-06-02, 2016-06-04) == (2016-06-02, 2016-06-05) : False False

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print \
    ...             ( "%s < %s : %5s; %s <= %s : %s"
    ...             % (r1, r2, r1 < r2, r1, r2, r1 <= r2)
    ...             )
    [2016-06-02, 2016-06-04] < [2016-06-02, 2016-06-05] :  True; [2016-06-02, 2016-06-04] <= [2016-06-02, 2016-06-05] : True
    [2016-06-02, 2016-06-04] < [2016-06-02, 2016-06-05) : False; [2016-06-02, 2016-06-04] <= [2016-06-02, 2016-06-05) : True
    [2016-06-02, 2016-06-04] < (2016-06-02, 2016-06-05] :  True; [2016-06-02, 2016-06-04] <= (2016-06-02, 2016-06-05] : True
    [2016-06-02, 2016-06-04] < (2016-06-02, 2016-06-05) :  True; [2016-06-02, 2016-06-04] <= (2016-06-02, 2016-06-05) : True
    [2016-06-02, 2016-06-04) < [2016-06-02, 2016-06-05] :  True; [2016-06-02, 2016-06-04) <= [2016-06-02, 2016-06-05] : True
    [2016-06-02, 2016-06-04) < [2016-06-02, 2016-06-05) :  True; [2016-06-02, 2016-06-04) <= [2016-06-02, 2016-06-05) : True
    [2016-06-02, 2016-06-04) < (2016-06-02, 2016-06-05] :  True; [2016-06-02, 2016-06-04) <= (2016-06-02, 2016-06-05] : True
    [2016-06-02, 2016-06-04) < (2016-06-02, 2016-06-05) :  True; [2016-06-02, 2016-06-04) <= (2016-06-02, 2016-06-05) : True
    (2016-06-02, 2016-06-04] < [2016-06-02, 2016-06-05] : False; (2016-06-02, 2016-06-04] <= [2016-06-02, 2016-06-05] : False
    (2016-06-02, 2016-06-04] < [2016-06-02, 2016-06-05) : False; (2016-06-02, 2016-06-04] <= [2016-06-02, 2016-06-05) : False
    (2016-06-02, 2016-06-04] < (2016-06-02, 2016-06-05] :  True; (2016-06-02, 2016-06-04] <= (2016-06-02, 2016-06-05] : True
    (2016-06-02, 2016-06-04] < (2016-06-02, 2016-06-05) : False; (2016-06-02, 2016-06-04] <= (2016-06-02, 2016-06-05) : True
    (2016-06-02, 2016-06-04) < [2016-06-02, 2016-06-05] : False; (2016-06-02, 2016-06-04) <= [2016-06-02, 2016-06-05] : False
    (2016-06-02, 2016-06-04) < [2016-06-02, 2016-06-05) : False; (2016-06-02, 2016-06-04) <= [2016-06-02, 2016-06-05) : False
    (2016-06-02, 2016-06-04) < (2016-06-02, 2016-06-05] :  True; (2016-06-02, 2016-06-04) <= (2016-06-02, 2016-06-05] : True
    (2016-06-02, 2016-06-04) < (2016-06-02, 2016-06-05) :  True; (2016-06-02, 2016-06-04) <= (2016-06-02, 2016-06-05) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "in", r2, ":", r1 in r2)
    [2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-04] : True
    [2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-04) : False
    [2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-04] : False
    [2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-04) : False
    [2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-04] : True
    [2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-04) : True
    [2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-04] : False
    [2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-04) : False
    (2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-04] : True
    (2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-04) : False
    (2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-04] : True
    (2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-04) : False
    (2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-04] : True
    (2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-04) : True
    (2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-04] : True
    (2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-04) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "in", r2, ":", r1 in r2, "<->", r2 in r1)
    [2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-05] : True <-> False
    [2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-05) : True <-> True
    [2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-05] : False <-> False
    [2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-05) : False <-> True
    [2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-05] : True <-> False
    [2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-05) : True <-> False
    [2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-05] : False <-> False
    [2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-05) : False <-> False
    (2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-05] : True <-> False
    (2016-06-02, 2016-06-04] in [2016-06-02, 2016-06-05) : True <-> False
    (2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-05] : True <-> False
    (2016-06-02, 2016-06-04] in (2016-06-02, 2016-06-05) : True <-> True
    (2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-05] : True <-> False
    (2016-06-02, 2016-06-04) in [2016-06-02, 2016-06-05) : True <-> False
    (2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-05] : True <-> False
    (2016-06-02, 2016-06-04) in (2016-06-02, 2016-06-05) : True <-> False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ab (R (d2, d3, bt1), R (d1, d2, bt2))
    ...         _show_ab (R (d3, d5, bt1), R (d1, d3, bt2))
    ...         _show_ab (R (d4, d6, bt1), R (d1, d3, bt2))
    [2016-06-02, 2016-06-03] after [2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05] after [2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06] after [2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03] after [2016-06-01, 2016-06-02) :  True
    [2016-06-03, 2016-06-05] after [2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06] after [2016-06-01, 2016-06-03) :  True
    [2016-06-02, 2016-06-03] after (2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05] after (2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06] after (2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03] after (2016-06-01, 2016-06-02) : False
    [2016-06-03, 2016-06-05] after (2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06] after (2016-06-01, 2016-06-03) :  True
    [2016-06-02, 2016-06-03) after [2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05) after [2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06) after [2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03) after [2016-06-01, 2016-06-02) :  True
    [2016-06-03, 2016-06-05) after [2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06) after [2016-06-01, 2016-06-03) :  True
    [2016-06-02, 2016-06-03) after (2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05) after (2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06) after (2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03) after (2016-06-01, 2016-06-02) : False
    [2016-06-03, 2016-06-05) after (2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06) after (2016-06-01, 2016-06-03) :  True
    (2016-06-02, 2016-06-03] after [2016-06-01, 2016-06-02] :  True
    (2016-06-03, 2016-06-05] after [2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06] after [2016-06-01, 2016-06-03] :  True
    (2016-06-02, 2016-06-03] after [2016-06-01, 2016-06-02) :  True
    (2016-06-03, 2016-06-05] after [2016-06-01, 2016-06-03) :  True
    (2016-06-04, 2016-06-06] after [2016-06-01, 2016-06-03) :  True
    (2016-06-02, 2016-06-03] after (2016-06-01, 2016-06-02] :  True
    (2016-06-03, 2016-06-05] after (2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06] after (2016-06-01, 2016-06-03] :  True
    (2016-06-02, 2016-06-03] after (2016-06-01, 2016-06-02) : False
    (2016-06-03, 2016-06-05] after (2016-06-01, 2016-06-03) :  True
    (2016-06-04, 2016-06-06] after (2016-06-01, 2016-06-03) :  True
    (2016-06-02, 2016-06-03) after [2016-06-01, 2016-06-02] : False
    (2016-06-03, 2016-06-05) after [2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06) after [2016-06-01, 2016-06-03] :  True
    (2016-06-02, 2016-06-03) after [2016-06-01, 2016-06-02) : False
    (2016-06-03, 2016-06-05) after [2016-06-01, 2016-06-03) :  True
    (2016-06-04, 2016-06-06) after [2016-06-01, 2016-06-03) :  True
    (2016-06-02, 2016-06-03) after (2016-06-01, 2016-06-02] : False
    (2016-06-03, 2016-06-05) after (2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06) after (2016-06-01, 2016-06-03] :  True
    (2016-06-02, 2016-06-03) after (2016-06-01, 2016-06-02) : False
    (2016-06-03, 2016-06-05) after (2016-06-01, 2016-06-03) :  True
    (2016-06-04, 2016-06-06) after (2016-06-01, 2016-06-03) :  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_adj (R (d2, d3, bt1), R (d1, d2, bt2))
    ...         _show_adj (R (d3, d5, bt1), R (d1, d3, bt2))
    ...         _show_adj (R (d4, d6, bt1), R (d1, d3, bt2))
    [2016-06-02, 2016-06-03] is_adjacent [2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05] is_adjacent [2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06] is_adjacent [2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03] is_adjacent [2016-06-01, 2016-06-02) :  True
    [2016-06-03, 2016-06-05] is_adjacent [2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06] is_adjacent [2016-06-01, 2016-06-03) : False
    [2016-06-02, 2016-06-03] is_adjacent (2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05] is_adjacent (2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06] is_adjacent (2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03] is_adjacent (2016-06-01, 2016-06-02) : False
    [2016-06-03, 2016-06-05] is_adjacent (2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06] is_adjacent (2016-06-01, 2016-06-03) : False
    [2016-06-02, 2016-06-03) is_adjacent [2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05) is_adjacent [2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06) is_adjacent [2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03) is_adjacent [2016-06-01, 2016-06-02) :  True
    [2016-06-03, 2016-06-05) is_adjacent [2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06) is_adjacent [2016-06-01, 2016-06-03) : False
    [2016-06-02, 2016-06-03) is_adjacent (2016-06-01, 2016-06-02] : False
    [2016-06-03, 2016-06-05) is_adjacent (2016-06-01, 2016-06-03] : False
    [2016-06-04, 2016-06-06) is_adjacent (2016-06-01, 2016-06-03] :  True
    [2016-06-02, 2016-06-03) is_adjacent (2016-06-01, 2016-06-02) : False
    [2016-06-03, 2016-06-05) is_adjacent (2016-06-01, 2016-06-03) :  True
    [2016-06-04, 2016-06-06) is_adjacent (2016-06-01, 2016-06-03) : False
    (2016-06-02, 2016-06-03] is_adjacent [2016-06-01, 2016-06-02] :  True
    (2016-06-03, 2016-06-05] is_adjacent [2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06] is_adjacent [2016-06-01, 2016-06-03] : False
    (2016-06-02, 2016-06-03] is_adjacent [2016-06-01, 2016-06-02) : False
    (2016-06-03, 2016-06-05] is_adjacent [2016-06-01, 2016-06-03) : False
    (2016-06-04, 2016-06-06] is_adjacent [2016-06-01, 2016-06-03) : False
    (2016-06-02, 2016-06-03] is_adjacent (2016-06-01, 2016-06-02] :  True
    (2016-06-03, 2016-06-05] is_adjacent (2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06] is_adjacent (2016-06-01, 2016-06-03] : False
    (2016-06-02, 2016-06-03] is_adjacent (2016-06-01, 2016-06-02) : False
    (2016-06-03, 2016-06-05] is_adjacent (2016-06-01, 2016-06-03) : False
    (2016-06-04, 2016-06-06] is_adjacent (2016-06-01, 2016-06-03) : False
    (2016-06-02, 2016-06-03) is_adjacent [2016-06-01, 2016-06-02] : False
    (2016-06-03, 2016-06-05) is_adjacent [2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06) is_adjacent [2016-06-01, 2016-06-03] : False
    (2016-06-02, 2016-06-03) is_adjacent [2016-06-01, 2016-06-02) : False
    (2016-06-03, 2016-06-05) is_adjacent [2016-06-01, 2016-06-03) : False
    (2016-06-04, 2016-06-06) is_adjacent [2016-06-01, 2016-06-03) : False
    (2016-06-02, 2016-06-03) is_adjacent (2016-06-01, 2016-06-02] : False
    (2016-06-03, 2016-06-05) is_adjacent (2016-06-01, 2016-06-03] :  True
    (2016-06-04, 2016-06-06) is_adjacent (2016-06-01, 2016-06-03] : False
    (2016-06-02, 2016-06-03) is_adjacent (2016-06-01, 2016-06-02) : False
    (2016-06-03, 2016-06-05) is_adjacent (2016-06-01, 2016-06-03) : False
    (2016-06-04, 2016-06-06) is_adjacent (2016-06-01, 2016-06-03) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (d3, d5, bt1), R (d1, d3, bt2))
    [2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-03] :  True
    [2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-03) : False
    [2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-03] :  True
    [2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-03) : False
    [2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-03] :  True
    [2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-03) : False
    [2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-03] :  True
    [2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-03) : False
    (2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-03] : False
    (2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-03) : False
    (2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-03] : False
    (2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-03) : False
    (2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-03] : False
    (2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-03) : False
    (2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-03] : False
    (2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-03) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (d3, d5, bt1), R (d1, d4, bt2))
    [2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-04] :  True
    [2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-04) :  True
    [2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-04] :  True
    [2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-04) :  True
    [2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-04] :  True
    [2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-04) :  True
    [2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-04] :  True
    [2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-04) :  True
    (2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-04] :  True
    (2016-06-03, 2016-06-05] overlaps [2016-06-01, 2016-06-04) : False
    (2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-04] :  True
    (2016-06-03, 2016-06-05] overlaps (2016-06-01, 2016-06-04) : False
    (2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-04] :  True
    (2016-06-03, 2016-06-05) overlaps [2016-06-01, 2016-06-04) : False
    (2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-04] :  True
    (2016-06-03, 2016-06-05) overlaps (2016-06-01, 2016-06-04) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (d3, d5, bt1), R (d1, d3, bt2))
    [2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-03] : [2016-06-03, 2016-06-03]
    [2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    [2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-03] : [2016-06-03, 2016-06-03]
    [2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    [2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-03] : [2016-06-03, 2016-06-03]
    [2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    [2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-03] : [2016-06-03, 2016-06-03]
    [2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (d3, d5, bt1), R (d1, d4, bt2))
    [2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-04] : [2016-06-03, 2016-06-04]
    [2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-04) : [2016-06-03, 2016-06-03]
    [2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-04] : [2016-06-03, 2016-06-04]
    [2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-04) : [2016-06-03, 2016-06-03]
    [2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-04] : [2016-06-03, 2016-06-04]
    [2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-04) : [2016-06-03, 2016-06-03]
    [2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-04] : [2016-06-03, 2016-06-04]
    [2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-04) : [2016-06-03, 2016-06-03]
    (2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-04] : [2016-06-04, 2016-06-04]
    (2016-06-03, 2016-06-05] intersection [2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)
    (2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-04] : [2016-06-04, 2016-06-04]
    (2016-06-03, 2016-06-05] intersection (2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)
    (2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-04] : [2016-06-04, 2016-06-04]
    (2016-06-03, 2016-06-05) intersection [2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)
    (2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-04] : [2016-06-04, 2016-06-04]
    (2016-06-03, 2016-06-05) intersection (2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (d3, d5, bt1), R (d1, d3, bt2))
    [2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-03] : [2016-06-01, 2016-06-05]
    [2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    [2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-03] : (2016-06-01, 2016-06-05]
    [2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    [2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-03] : [2016-06-01, 2016-06-05)
    [2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    [2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-03] : (2016-06-01, 2016-06-05)
    [2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-03] : (2016-06-03, 2016-06-03)
    (2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-03) : (2016-06-03, 2016-06-03)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (d3, d5, bt1), R (d1, d4, bt2))
    [2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-04] : [2016-06-01, 2016-06-05]
    [2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-04) : [2016-06-01, 2016-06-05]
    [2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-04] : (2016-06-01, 2016-06-05]
    [2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-04) : (2016-06-01, 2016-06-05]
    [2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-04] : [2016-06-01, 2016-06-04]
    [2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-04) : [2016-06-01, 2016-06-05)
    [2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-04] : (2016-06-01, 2016-06-04]
    [2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-04) : (2016-06-01, 2016-06-05)
    (2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-04] : [2016-06-01, 2016-06-05]
    (2016-06-03, 2016-06-05] union [2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)
    (2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-04] : (2016-06-01, 2016-06-05]
    (2016-06-03, 2016-06-05] union (2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)
    (2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-04] : [2016-06-01, 2016-06-04]
    (2016-06-03, 2016-06-05) union [2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)
    (2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-04] : (2016-06-01, 2016-06-04]
    (2016-06-03, 2016-06-05) union (2016-06-01, 2016-06-04) : (2016-06-04, 2016-06-03)

    >>> for bt in ("  ", "[]", "[)", "(]", "()") :
    ...     s = " ".join ((bt [0], "2016-06-03, 2016-06-05", bt[1]))
    ...     _show_fs (R, s)
      2016-06-03, 2016-06-05   : Date_Range (datetime.date(2016, 6, 3), datetime.date(2016, 6, 5), '[)')
    [ 2016-06-03, 2016-06-05 ] : Date_Range (datetime.date(2016, 6, 3), datetime.date(2016, 6, 5), '[]')
    [ 2016-06-03, 2016-06-05 ) : Date_Range (datetime.date(2016, 6, 3), datetime.date(2016, 6, 5), '[)')
    ( 2016-06-03, 2016-06-05 ] : Date_Range (datetime.date(2016, 6, 3), datetime.date(2016, 6, 5), '(]')
    ( 2016-06-03, 2016-06-05 ) : Date_Range (datetime.date(2016, 6, 3), datetime.date(2016, 6, 5), '()')

    >>> rs = ("23.6.2016, 27.Jun.2016", "(2016-07-03, ]", "[None, 2016-07-03]")
    >>> for r in rs :
    ...     _show_fs (R, r)
    23.6.2016, 27.Jun.2016 : Date_Range (datetime.date(2016, 6, 23), datetime.date(2016, 6, 27), '[)')
    (2016-07-03, ] : Date_Range (datetime.date(2016, 7, 3), None, '(]')
    [None, 2016-07-03] : Date_Range (None, datetime.date(2016, 7, 3), '[]')

""" ### _test_date_range

_test_time_range = r"""

    >>> from _TFL.Range import _show_ab, _show_adj, _show_fs, _show_intersection, _show_ovl, _show_sb, _show_union

    >>> R   = Time_Range
    >>> dtt = R.S_Type

    >>> infinite = R ()
    >>> infinite_l = R (None, dtt (8))
    >>> infinite_u = R (dtt (8), None)
    >>> infinite
    Time_Range (None, None, '[)')
    >>> print (infinite, infinite_l, infinite_u)
    [None, None) [None, 08:00) [08:00, None)
    >>> bool (infinite), bool (infinite_l), bool (infinite_u)
    (True, True, True)
    >>> infinite in infinite, infinite_l in infinite, infinite_u in infinite
    (True, True, True)
    >>> infinite in infinite_l, infinite in infinite_u, infinite_l in infinite_u
    (False, False, False)
    >>> print (portable_repr ((infinite.duration, infinite_l.duration, infinite_u.duration)))
    (86399999999, 28800000000, 57599999999)

    >>> empty = R (dtt (8), dtt (8))
    >>> empty
    Time_Range (datetime.time(8, 0), datetime.time(8, 0), '[)')
    >>> print (empty)
    [08:00, 08:00)
    >>> bool (empty), empty.is_empty
    (False, True)
    >>> empty.LB.bound, empty.LB.first, empty.LB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(0, 0))
    >>> empty.UB.bound, empty.UB.first, empty.UB.inf
    (datetime.time(8, 0), datetime.time(7, 59, 59, 999999), datetime.time(23, 59, 59, 999999))
    >>> empty in infinite, empty in infinite_l, empty in infinite_u
    (False, False, False)
    >>> empty.duration
    0

    >>> point = R (empty.lower, empty.upper, "[]")
    >>> point
    Time_Range (datetime.time(8, 0), datetime.time(8, 0), '[]')
    >>> print (point)
    [08:00, 08:00]
    >>> bool (point)
    True
    >>> point.LB.bound, point.LB.first, point.LB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(0, 0))
    >>> point.UB.bound, point.UB.first, point.UB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(23, 59, 59, 999999))
    >>> point in infinite, point in infinite_l, point in infinite_u
    (True, False, True)
    >>> point.duration
    1

    >>> point_x = R (point.lower, dtt (9), "[)")
    >>> point_x
    Time_Range (datetime.time(8, 0), datetime.time(9, 0), '[)')
    >>> print (point_x)
    [08:00, 09:00)
    >>> bool (point_x)
    True
    >>> point_x.LB.bound, point_x.LB.first, point_x.LB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(0, 0))
    >>> point_x.UB.bound, point_x.UB.first, point_x.UB.inf
    (datetime.time(9, 0), datetime.time(8, 59, 59, 999999), datetime.time(23, 59, 59, 999999))
    >>> point_x in infinite, point_x in infinite_l, point_x in infinite_u
    (True, False, True)
    >>> point_x.duration
    3600000000

    >>> ii_24 = R (dtt (2), dtt (4), "[]")
    >>> ix_24 = R (dtt (2), dtt (4), "[)")
    >>> xi_24 = R (dtt (2), dtt (4), "(]")
    >>> xx_24 = R (dtt (2), dtt (4), "()")
    >>> ii_25 = R (dtt (2), dtt (5), "[]")
    >>> ix_25 = R (dtt (2), dtt (5), "[)")
    >>> xi_25 = R (dtt (2), dtt (5), "(]")
    >>> xx_25 = R (dtt (2), dtt (5), "()")

    >>> for r in (point, point_x, ii_24) :
    ...     print (r.FO, r.FO.lower, r.FO.upper)
    [08:00, 08:00] 08:00 08:00
    [08:00, 09:00) 08:00 09:00
    [02:00, 04:00] 02:00 04:00

    >>> for r in (ii_24, ix_24, xi_24, xx_24) :
    ...     print (r, r.duration)
    [02:00, 04:00] 7200000001
    [02:00, 04:00) 7200000000
    (02:00, 04:00] 7200000000
    (02:00, 04:00) 7199999999

    >>> for i in range (2, 5) :
    ...     v = dtt (i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (v, "in", r, ":", v in r)
    02:00:00 in [02:00, 04:00] : True
    02:00:00 in [02:00, 04:00) : True
    02:00:00 in (02:00, 04:00] : False
    02:00:00 in (02:00, 04:00) : False
    03:00:00 in [02:00, 04:00] : True
    03:00:00 in [02:00, 04:00) : True
    03:00:00 in (02:00, 04:00] : True
    03:00:00 in (02:00, 04:00) : True
    04:00:00 in [02:00, 04:00] : True
    04:00:00 in [02:00, 04:00) : False
    04:00:00 in (02:00, 04:00] : True
    04:00:00 in (02:00, 04:00) : False

    >>> for i in range (2, 5) :
    ...     v = R.D_Type (hours = i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r, "+", v, ":", r + v, "" if v+r == r+v else "*** + isn't communitative ***")
    [02:00, 04:00] + 2:00:00 : [04:00, 06:00]
    [02:00, 04:00) + 2:00:00 : [04:00, 06:00)
    (02:00, 04:00] + 2:00:00 : (04:00, 06:00]
    (02:00, 04:00) + 2:00:00 : (04:00, 06:00)
    [02:00, 04:00] + 3:00:00 : [05:00, 07:00]
    [02:00, 04:00) + 3:00:00 : [05:00, 07:00)
    (02:00, 04:00] + 3:00:00 : (05:00, 07:00]
    (02:00, 04:00) + 3:00:00 : (05:00, 07:00)
    [02:00, 04:00] + 4:00:00 : [06:00, 08:00]
    [02:00, 04:00) + 4:00:00 : [06:00, 08:00)
    (02:00, 04:00] + 4:00:00 : (06:00, 08:00]
    (02:00, 04:00) + 4:00:00 : (06:00, 08:00)

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [02:00, 04:00] == [02:00, 04:00] : True True
    [02:00, 04:00] == [02:00, 04:00) : False False
    [02:00, 04:00] == (02:00, 04:00] : False False
    [02:00, 04:00] == (02:00, 04:00) : False False
    [02:00, 04:00) == [02:00, 04:00] : False False
    [02:00, 04:00) == [02:00, 04:00) : True True
    [02:00, 04:00) == (02:00, 04:00] : False False
    [02:00, 04:00) == (02:00, 04:00) : False False
    (02:00, 04:00] == [02:00, 04:00] : False False
    (02:00, 04:00] == [02:00, 04:00) : False False
    (02:00, 04:00] == (02:00, 04:00] : True True
    (02:00, 04:00] == (02:00, 04:00) : False False
    (02:00, 04:00) == [02:00, 04:00] : False False
    (02:00, 04:00) == [02:00, 04:00) : False False
    (02:00, 04:00) == (02:00, 04:00] : False False
    (02:00, 04:00) == (02:00, 04:00) : True True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [02:00, 04:00] == [02:00, 05:00] : False False
    [02:00, 04:00] == [02:00, 05:00) : False False
    [02:00, 04:00] == (02:00, 05:00] : False False
    [02:00, 04:00] == (02:00, 05:00) : False False
    [02:00, 04:00) == [02:00, 05:00] : False False
    [02:00, 04:00) == [02:00, 05:00) : False False
    [02:00, 04:00) == (02:00, 05:00] : False False
    [02:00, 04:00) == (02:00, 05:00) : False False
    (02:00, 04:00] == [02:00, 05:00] : False False
    (02:00, 04:00] == [02:00, 05:00) : False False
    (02:00, 04:00] == (02:00, 05:00] : False False
    (02:00, 04:00] == (02:00, 05:00) : False False
    (02:00, 04:00) == [02:00, 05:00] : False False
    (02:00, 04:00) == [02:00, 05:00) : False False
    (02:00, 04:00) == (02:00, 05:00] : False False
    (02:00, 04:00) == (02:00, 05:00) : False False

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print \
    ...             ( "%s < %s : %5s; %s <= %s : %s"
    ...             % (r1, r2, r1 < r2, r1, r2, r1 <= r2)
    ...             )
    [02:00, 04:00] < [02:00, 05:00] :  True; [02:00, 04:00] <= [02:00, 05:00] : True
    [02:00, 04:00] < [02:00, 05:00) :  True; [02:00, 04:00] <= [02:00, 05:00) : True
    [02:00, 04:00] < (02:00, 05:00] :  True; [02:00, 04:00] <= (02:00, 05:00] : True
    [02:00, 04:00] < (02:00, 05:00) :  True; [02:00, 04:00] <= (02:00, 05:00) : True
    [02:00, 04:00) < [02:00, 05:00] :  True; [02:00, 04:00) <= [02:00, 05:00] : True
    [02:00, 04:00) < [02:00, 05:00) :  True; [02:00, 04:00) <= [02:00, 05:00) : True
    [02:00, 04:00) < (02:00, 05:00] :  True; [02:00, 04:00) <= (02:00, 05:00] : True
    [02:00, 04:00) < (02:00, 05:00) :  True; [02:00, 04:00) <= (02:00, 05:00) : True
    (02:00, 04:00] < [02:00, 05:00] : False; (02:00, 04:00] <= [02:00, 05:00] : False
    (02:00, 04:00] < [02:00, 05:00) : False; (02:00, 04:00] <= [02:00, 05:00) : False
    (02:00, 04:00] < (02:00, 05:00] :  True; (02:00, 04:00] <= (02:00, 05:00] : True
    (02:00, 04:00] < (02:00, 05:00) :  True; (02:00, 04:00] <= (02:00, 05:00) : True
    (02:00, 04:00) < [02:00, 05:00] : False; (02:00, 04:00) <= [02:00, 05:00] : False
    (02:00, 04:00) < [02:00, 05:00) : False; (02:00, 04:00) <= [02:00, 05:00) : False
    (02:00, 04:00) < (02:00, 05:00] :  True; (02:00, 04:00) <= (02:00, 05:00] : True
    (02:00, 04:00) < (02:00, 05:00) :  True; (02:00, 04:00) <= (02:00, 05:00) : True

    >>> for r1 in (ii_25, ix_25, xi_25, xx_25) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print \
    ...             ( "%s > %s : %5s; %s >= %s : %s"
    ...             % (r1, r2, r1 > r2, r1, r2, r1 >= r2)
    ...             )
    [02:00, 05:00] > [02:00, 04:00] :  True; [02:00, 05:00] >= [02:00, 04:00] : True
    [02:00, 05:00] > [02:00, 04:00) :  True; [02:00, 05:00] >= [02:00, 04:00) : True
    [02:00, 05:00] > (02:00, 04:00] : False; [02:00, 05:00] >= (02:00, 04:00] : False
    [02:00, 05:00] > (02:00, 04:00) : False; [02:00, 05:00] >= (02:00, 04:00) : False
    [02:00, 05:00) > [02:00, 04:00] :  True; [02:00, 05:00) >= [02:00, 04:00] : True
    [02:00, 05:00) > [02:00, 04:00) :  True; [02:00, 05:00) >= [02:00, 04:00) : True
    [02:00, 05:00) > (02:00, 04:00] : False; [02:00, 05:00) >= (02:00, 04:00] : False
    [02:00, 05:00) > (02:00, 04:00) : False; [02:00, 05:00) >= (02:00, 04:00) : False
    (02:00, 05:00] > [02:00, 04:00] :  True; (02:00, 05:00] >= [02:00, 04:00] : True
    (02:00, 05:00] > [02:00, 04:00) :  True; (02:00, 05:00] >= [02:00, 04:00) : True
    (02:00, 05:00] > (02:00, 04:00] :  True; (02:00, 05:00] >= (02:00, 04:00] : True
    (02:00, 05:00] > (02:00, 04:00) :  True; (02:00, 05:00] >= (02:00, 04:00) : True
    (02:00, 05:00) > [02:00, 04:00] :  True; (02:00, 05:00) >= [02:00, 04:00] : True
    (02:00, 05:00) > [02:00, 04:00) :  True; (02:00, 05:00) >= [02:00, 04:00) : True
    (02:00, 05:00) > (02:00, 04:00] :  True; (02:00, 05:00) >= (02:00, 04:00] : True
    (02:00, 05:00) > (02:00, 04:00) :  True; (02:00, 05:00) >= (02:00, 04:00) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "in", r2, ":", r1 in r2)
    [02:00, 04:00] in [02:00, 04:00] : True
    [02:00, 04:00] in [02:00, 04:00) : False
    [02:00, 04:00] in (02:00, 04:00] : False
    [02:00, 04:00] in (02:00, 04:00) : False
    [02:00, 04:00) in [02:00, 04:00] : True
    [02:00, 04:00) in [02:00, 04:00) : True
    [02:00, 04:00) in (02:00, 04:00] : False
    [02:00, 04:00) in (02:00, 04:00) : False
    (02:00, 04:00] in [02:00, 04:00] : True
    (02:00, 04:00] in [02:00, 04:00) : False
    (02:00, 04:00] in (02:00, 04:00] : True
    (02:00, 04:00] in (02:00, 04:00) : False
    (02:00, 04:00) in [02:00, 04:00] : True
    (02:00, 04:00) in [02:00, 04:00) : True
    (02:00, 04:00) in (02:00, 04:00] : True
    (02:00, 04:00) in (02:00, 04:00) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "in", r2, ":", r1 in r2, "<->", r2 in r1)
    [02:00, 04:00] in [02:00, 05:00] : True <-> False
    [02:00, 04:00] in [02:00, 05:00) : True <-> False
    [02:00, 04:00] in (02:00, 05:00] : False <-> False
    [02:00, 04:00] in (02:00, 05:00) : False <-> False
    [02:00, 04:00) in [02:00, 05:00] : True <-> False
    [02:00, 04:00) in [02:00, 05:00) : True <-> False
    [02:00, 04:00) in (02:00, 05:00] : False <-> False
    [02:00, 04:00) in (02:00, 05:00) : False <-> False
    (02:00, 04:00] in [02:00, 05:00] : True <-> False
    (02:00, 04:00] in [02:00, 05:00) : True <-> False
    (02:00, 04:00] in (02:00, 05:00] : True <-> False
    (02:00, 04:00] in (02:00, 05:00) : True <-> False
    (02:00, 04:00) in [02:00, 05:00] : True <-> False
    (02:00, 04:00) in [02:00, 05:00) : True <-> False
    (02:00, 04:00) in (02:00, 05:00] : True <-> False
    (02:00, 04:00) in (02:00, 05:00) : True <-> False

    >>> for i in range (1, 4) :
    ...     for bs in ("[]", "[)", "(]", "()") :
    ...         r = R (dtt (1), dtt (i), bs)
    ...         print \
    ...             ( "r : %s %5s; 1 in r: %5s; 2 in r: %5s"
    ...             % (r, bool (r), dtt (1) in r, dtt (2) in r)
    ...             )
    r : [01:00, 01:00]  True; 1 in r:  True; 2 in r: False
    r : [01:00, 01:00) False; 1 in r: False; 2 in r: False
    r : (01:00, 01:00] False; 1 in r: False; 2 in r: False
    r : (01:00, 01:00) False; 1 in r: False; 2 in r: False
    r : [01:00, 02:00]  True; 1 in r:  True; 2 in r:  True
    r : [01:00, 02:00)  True; 1 in r:  True; 2 in r: False
    r : (01:00, 02:00]  True; 1 in r: False; 2 in r:  True
    r : (01:00, 02:00)  True; 1 in r: False; 2 in r: False
    r : [01:00, 03:00]  True; 1 in r:  True; 2 in r:  True
    r : [01:00, 03:00)  True; 1 in r:  True; 2 in r:  True
    r : (01:00, 03:00]  True; 1 in r: False; 2 in r:  True
    r : (01:00, 03:00)  True; 1 in r: False; 2 in r:  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ab (R (dtt (2), dtt (3), bt1), R (dtt (1), dtt (2), bt2))
    ...         _show_ab (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    ...         _show_ab (R (dtt (4), dtt (6), bt1), R (dtt (1), dtt (3), bt2))
    [02:00, 03:00] after [01:00, 02:00] : False
    [03:00, 05:00] after [01:00, 03:00] : False
    [04:00, 06:00] after [01:00, 03:00] :  True
    [02:00, 03:00] after [01:00, 02:00) :  True
    [03:00, 05:00] after [01:00, 03:00) :  True
    [04:00, 06:00] after [01:00, 03:00) :  True
    [02:00, 03:00] after (01:00, 02:00] : False
    [03:00, 05:00] after (01:00, 03:00] : False
    [04:00, 06:00] after (01:00, 03:00] :  True
    [02:00, 03:00] after (01:00, 02:00) :  True
    [03:00, 05:00] after (01:00, 03:00) :  True
    [04:00, 06:00] after (01:00, 03:00) :  True
    [02:00, 03:00) after [01:00, 02:00] : False
    [03:00, 05:00) after [01:00, 03:00] : False
    [04:00, 06:00) after [01:00, 03:00] :  True
    [02:00, 03:00) after [01:00, 02:00) :  True
    [03:00, 05:00) after [01:00, 03:00) :  True
    [04:00, 06:00) after [01:00, 03:00) :  True
    [02:00, 03:00) after (01:00, 02:00] : False
    [03:00, 05:00) after (01:00, 03:00] : False
    [04:00, 06:00) after (01:00, 03:00] :  True
    [02:00, 03:00) after (01:00, 02:00) :  True
    [03:00, 05:00) after (01:00, 03:00) :  True
    [04:00, 06:00) after (01:00, 03:00) :  True
    (02:00, 03:00] after [01:00, 02:00] :  True
    (03:00, 05:00] after [01:00, 03:00] :  True
    (04:00, 06:00] after [01:00, 03:00] :  True
    (02:00, 03:00] after [01:00, 02:00) :  True
    (03:00, 05:00] after [01:00, 03:00) :  True
    (04:00, 06:00] after [01:00, 03:00) :  True
    (02:00, 03:00] after (01:00, 02:00] :  True
    (03:00, 05:00] after (01:00, 03:00] :  True
    (04:00, 06:00] after (01:00, 03:00] :  True
    (02:00, 03:00] after (01:00, 02:00) :  True
    (03:00, 05:00] after (01:00, 03:00) :  True
    (04:00, 06:00] after (01:00, 03:00) :  True
    (02:00, 03:00) after [01:00, 02:00] :  True
    (03:00, 05:00) after [01:00, 03:00] :  True
    (04:00, 06:00) after [01:00, 03:00] :  True
    (02:00, 03:00) after [01:00, 02:00) :  True
    (03:00, 05:00) after [01:00, 03:00) :  True
    (04:00, 06:00) after [01:00, 03:00) :  True
    (02:00, 03:00) after (01:00, 02:00] :  True
    (03:00, 05:00) after (01:00, 03:00] :  True
    (04:00, 06:00) after (01:00, 03:00] :  True
    (02:00, 03:00) after (01:00, 02:00) :  True
    (03:00, 05:00) after (01:00, 03:00) :  True
    (04:00, 06:00) after (01:00, 03:00) :  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_adj (R (dtt (2), dtt (3), bt1), R (dtt (1), dtt (2), bt2))
    ...         _show_adj (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    ...         _show_adj (R (dtt (4), dtt (6), bt1), R (dtt (1), dtt (3), bt2))
    [02:00, 03:00] is_adjacent [01:00, 02:00] : False
    [03:00, 05:00] is_adjacent [01:00, 03:00] : False
    [04:00, 06:00] is_adjacent [01:00, 03:00] : False
    [02:00, 03:00] is_adjacent [01:00, 02:00) :  True
    [03:00, 05:00] is_adjacent [01:00, 03:00) :  True
    [04:00, 06:00] is_adjacent [01:00, 03:00) : False
    [02:00, 03:00] is_adjacent (01:00, 02:00] : False
    [03:00, 05:00] is_adjacent (01:00, 03:00] : False
    [04:00, 06:00] is_adjacent (01:00, 03:00] : False
    [02:00, 03:00] is_adjacent (01:00, 02:00) :  True
    [03:00, 05:00] is_adjacent (01:00, 03:00) :  True
    [04:00, 06:00] is_adjacent (01:00, 03:00) : False
    [02:00, 03:00) is_adjacent [01:00, 02:00] : False
    [03:00, 05:00) is_adjacent [01:00, 03:00] : False
    [04:00, 06:00) is_adjacent [01:00, 03:00] : False
    [02:00, 03:00) is_adjacent [01:00, 02:00) :  True
    [03:00, 05:00) is_adjacent [01:00, 03:00) :  True
    [04:00, 06:00) is_adjacent [01:00, 03:00) : False
    [02:00, 03:00) is_adjacent (01:00, 02:00] : False
    [03:00, 05:00) is_adjacent (01:00, 03:00] : False
    [04:00, 06:00) is_adjacent (01:00, 03:00] : False
    [02:00, 03:00) is_adjacent (01:00, 02:00) :  True
    [03:00, 05:00) is_adjacent (01:00, 03:00) :  True
    [04:00, 06:00) is_adjacent (01:00, 03:00) : False
    (02:00, 03:00] is_adjacent [01:00, 02:00] :  True
    (03:00, 05:00] is_adjacent [01:00, 03:00] :  True
    (04:00, 06:00] is_adjacent [01:00, 03:00] : False
    (02:00, 03:00] is_adjacent [01:00, 02:00) : False
    (03:00, 05:00] is_adjacent [01:00, 03:00) : False
    (04:00, 06:00] is_adjacent [01:00, 03:00) : False
    (02:00, 03:00] is_adjacent (01:00, 02:00] :  True
    (03:00, 05:00] is_adjacent (01:00, 03:00] :  True
    (04:00, 06:00] is_adjacent (01:00, 03:00] : False
    (02:00, 03:00] is_adjacent (01:00, 02:00) : False
    (03:00, 05:00] is_adjacent (01:00, 03:00) : False
    (04:00, 06:00] is_adjacent (01:00, 03:00) : False
    (02:00, 03:00) is_adjacent [01:00, 02:00] :  True
    (03:00, 05:00) is_adjacent [01:00, 03:00] :  True
    (04:00, 06:00) is_adjacent [01:00, 03:00] : False
    (02:00, 03:00) is_adjacent [01:00, 02:00) : False
    (03:00, 05:00) is_adjacent [01:00, 03:00) : False
    (04:00, 06:00) is_adjacent [01:00, 03:00) : False
    (02:00, 03:00) is_adjacent (01:00, 02:00] :  True
    (03:00, 05:00) is_adjacent (01:00, 03:00] :  True
    (04:00, 06:00) is_adjacent (01:00, 03:00] : False
    (02:00, 03:00) is_adjacent (01:00, 02:00) : False
    (03:00, 05:00) is_adjacent (01:00, 03:00) : False
    (04:00, 06:00) is_adjacent (01:00, 03:00) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    [03:00, 05:00] intersection [01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00] intersection [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00] intersection (01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00] intersection (01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) intersection [01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00) intersection [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) intersection (01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00) intersection (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] intersection [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] intersection [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] intersection (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] intersection (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) intersection [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) intersection [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) intersection (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) intersection (01:00, 03:00) : (03:00, 03:00)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (4), bt2))
    [03:00, 05:00] intersection [01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00] intersection [01:00, 04:00) : [03:00, 03:59:59.999999]
    [03:00, 05:00] intersection (01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00] intersection (01:00, 04:00) : [03:00, 03:59:59.999999]
    [03:00, 05:00) intersection [01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00) intersection [01:00, 04:00) : [03:00, 03:59:59.999999]
    [03:00, 05:00) intersection (01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00) intersection (01:00, 04:00) : [03:00, 03:59:59.999999]
    (03:00, 05:00] intersection [01:00, 04:00] : [03:00:00.000001, 04:00]
    (03:00, 05:00] intersection [01:00, 04:00) : [03:00:00.000001, 03:59:59.999999]
    (03:00, 05:00] intersection (01:00, 04:00] : [03:00:00.000001, 04:00]
    (03:00, 05:00] intersection (01:00, 04:00) : [03:00:00.000001, 03:59:59.999999]
    (03:00, 05:00) intersection [01:00, 04:00] : [03:00:00.000001, 04:00]
    (03:00, 05:00) intersection [01:00, 04:00) : [03:00:00.000001, 03:59:59.999999]
    (03:00, 05:00) intersection (01:00, 04:00] : [03:00:00.000001, 04:00]
    (03:00, 05:00) intersection (01:00, 04:00) : [03:00:00.000001, 03:59:59.999999]

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    [03:00, 05:00] union [01:00, 03:00] : [01:00, 05:00]
    [03:00, 05:00] union [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00] union (01:00, 03:00] : (01:00, 05:00]
    [03:00, 05:00] union (01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) union [01:00, 03:00] : [01:00, 05:00)
    [03:00, 05:00) union [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) union (01:00, 03:00] : (01:00, 05:00)
    [03:00, 05:00) union (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] union [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] union [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] union (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] union (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) union [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) union [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) union (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) union (01:00, 03:00) : (03:00, 03:00)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (4), bt2))
    [03:00, 05:00] union [01:00, 04:00] : [01:00, 05:00]
    [03:00, 05:00] union [01:00, 04:00) : [01:00, 05:00]
    [03:00, 05:00] union (01:00, 04:00] : (01:00, 05:00]
    [03:00, 05:00] union (01:00, 04:00) : (01:00, 05:00]
    [03:00, 05:00) union [01:00, 04:00] : [01:00, 05:00)
    [03:00, 05:00) union [01:00, 04:00) : [01:00, 05:00)
    [03:00, 05:00) union (01:00, 04:00] : (01:00, 05:00)
    [03:00, 05:00) union (01:00, 04:00) : (01:00, 05:00)
    (03:00, 05:00] union [01:00, 04:00] : [01:00, 05:00]
    (03:00, 05:00] union [01:00, 04:00) : [01:00, 05:00]
    (03:00, 05:00] union (01:00, 04:00] : (01:00, 05:00]
    (03:00, 05:00] union (01:00, 04:00) : (01:00, 05:00]
    (03:00, 05:00) union [01:00, 04:00] : [01:00, 05:00)
    (03:00, 05:00) union [01:00, 04:00) : [01:00, 05:00)
    (03:00, 05:00) union (01:00, 04:00] : (01:00, 05:00)
    (03:00, 05:00) union (01:00, 04:00) : (01:00, 05:00)

""" ### _test_time_range

_test_time_range_h = r"""

    >>> from _TFL.Range import _show_ab, _show_adj, _show_fs, _show_intersection, _show_ovl, _show_sb, _show_union

    >>> R   = Time_Range_H
    >>> dtt = R.S_Type
    >>> infinite = R ()
    >>> infinite_l = R (None, dtt (8))
    >>> infinite_u = R (dtt (8), None)
    >>> infinite
    Time_Range_H (None, None, '[)')
    >>> print (infinite, infinite_l, infinite_u)
    [None, None) [None, 08:00) [08:00, None)
    >>> bool (infinite), bool (infinite_l), bool (infinite_u)
    (True, True, True)
    >>> infinite in infinite, infinite_l in infinite, infinite_u in infinite
    (True, True, True)
    >>> infinite in infinite_l, infinite in infinite_u, infinite_l in infinite_u
    (False, False, False)
    >>> print (portable_repr ((infinite.duration, infinite_l.duration, infinite_u.duration)))
    (24, 8, 16)

    >>> empty = R (dtt (8), dtt (8))
    >>> empty
    Time_Range_H (datetime.time(8, 0), datetime.time(8, 0), '[)')
    >>> print (empty)
    [08:00, 08:00)
    >>> bool (empty), empty.is_empty
    (False, True)
    >>> empty.LB.bound, empty.LB.first, empty.LB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(0, 0))
    >>> empty.UB.bound, empty.UB.first, empty.UB.inf
    (datetime.time(8, 0), datetime.time(7, 0), datetime.time(23, 59, 59, 999999))
    >>> empty in infinite, empty in infinite_l, empty in infinite_u
    (False, False, False)
    >>> empty.duration
    0

    >>> point = R (empty.lower, empty.upper, "[]")
    >>> point
    Time_Range_H (datetime.time(8, 0), datetime.time(8, 0), '[]')
    >>> print (point)
    [08:00, 08:00]
    >>> bool (point)
    True
    >>> point.LB.bound, point.LB.first, point.LB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(0, 0))
    >>> point.UB.bound, point.UB.first, point.UB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(23, 59, 59, 999999))
    >>> point in infinite, point in infinite_l, point in infinite_u
    (True, False, True)
    >>> point.duration
    1

    >>> point_x = R (point.lower, dtt (9), "[)")
    >>> point_x
    Time_Range_H (datetime.time(8, 0), datetime.time(9, 0), '[)')
    >>> print (point_x)
    [08:00, 09:00)
    >>> bool (point_x)
    True
    >>> point_x.LB.bound, point_x.LB.first, point_x.LB.inf
    (datetime.time(8, 0), datetime.time(8, 0), datetime.time(0, 0))
    >>> point_x.UB.bound, point_x.UB.first, point_x.UB.inf
    (datetime.time(9, 0), datetime.time(8, 0), datetime.time(23, 59, 59, 999999))
    >>> point_x in infinite, point_x in infinite_l, point_x in infinite_u
    (True, False, True)
    >>> point_x.duration
    1

    >>> ii_24 = R (dtt (2), dtt (4), "[]")
    >>> ix_24 = R (dtt (2), dtt (4), "[)")
    >>> xi_24 = R (dtt (2), dtt (4), "(]")
    >>> xx_24 = R (dtt (2), dtt (4), "()")
    >>> ii_25 = R (dtt (2), dtt (5), "[]")
    >>> ix_25 = R (dtt (2), dtt (5), "[)")
    >>> xi_25 = R (dtt (2), dtt (5), "(]")
    >>> xx_25 = R (dtt (2), dtt (5), "()")

    >>> for r in (ii_24, ix_24, xi_24, xx_24) :
    ...     print (r, r.duration, tuple (r))
    [02:00, 04:00] 3 (datetime.time(2, 0), datetime.time(3, 0), datetime.time(4, 0))
    [02:00, 04:00) 2 (datetime.time(2, 0), datetime.time(3, 0))
    (02:00, 04:00] 2 (datetime.time(3, 0), datetime.time(4, 0))
    (02:00, 04:00) 1 (datetime.time(3, 0),)

    >>> for r in (ii_24, ix_24, xi_24, xx_24) :
    ...     print (r, portable_repr (r.range_pattern.match (pyk.text_type (r)).groupdict ()))
    [02:00, 04:00] {'LB' : '[', 'UB' : ']', 'lower' : '02:00', 'upper' : '04:00'}
    [02:00, 04:00) {'LB' : '[', 'UB' : ')', 'lower' : '02:00', 'upper' : '04:00'}
    (02:00, 04:00] {'LB' : '(', 'UB' : ']', 'lower' : '02:00', 'upper' : '04:00'}
    (02:00, 04:00) {'LB' : '(', 'UB' : ')', 'lower' : '02:00', 'upper' : '04:00'}

    >>> for i in range (2, 5) :
    ...     v = dtt (i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (v, "in", r, ":", v in r)
    02:00:00 in [02:00, 04:00] : True
    02:00:00 in [02:00, 04:00) : True
    02:00:00 in (02:00, 04:00] : False
    02:00:00 in (02:00, 04:00) : False
    03:00:00 in [02:00, 04:00] : True
    03:00:00 in [02:00, 04:00) : True
    03:00:00 in (02:00, 04:00] : True
    03:00:00 in (02:00, 04:00) : True
    04:00:00 in [02:00, 04:00] : True
    04:00:00 in [02:00, 04:00) : False
    04:00:00 in (02:00, 04:00] : True
    04:00:00 in (02:00, 04:00) : False

    >>> for i in range (2, 5) :
    ...     v = R.D_Type (hours = i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r, "+", v, ":", r + v, "" if v+r == r+v else "*** + isn't communitative ***")
    [02:00, 04:00] + 2:00:00 : [04:00, 06:00]
    [02:00, 04:00) + 2:00:00 : [04:00, 06:00)
    (02:00, 04:00] + 2:00:00 : (04:00, 06:00]
    (02:00, 04:00) + 2:00:00 : (04:00, 06:00)
    [02:00, 04:00] + 3:00:00 : [05:00, 07:00]
    [02:00, 04:00) + 3:00:00 : [05:00, 07:00)
    (02:00, 04:00] + 3:00:00 : (05:00, 07:00]
    (02:00, 04:00) + 3:00:00 : (05:00, 07:00)
    [02:00, 04:00] + 4:00:00 : [06:00, 08:00]
    [02:00, 04:00) + 4:00:00 : [06:00, 08:00)
    (02:00, 04:00] + 4:00:00 : (06:00, 08:00]
    (02:00, 04:00) + 4:00:00 : (06:00, 08:00)

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [02:00, 04:00] == [02:00, 04:00] : True True
    [02:00, 04:00] == [02:00, 04:00) : False False
    [02:00, 04:00] == (02:00, 04:00] : False False
    [02:00, 04:00] == (02:00, 04:00) : False False
    [02:00, 04:00) == [02:00, 04:00] : False False
    [02:00, 04:00) == [02:00, 04:00) : True True
    [02:00, 04:00) == (02:00, 04:00] : False False
    [02:00, 04:00) == (02:00, 04:00) : False False
    (02:00, 04:00] == [02:00, 04:00] : False False
    (02:00, 04:00] == [02:00, 04:00) : False False
    (02:00, 04:00] == (02:00, 04:00] : True True
    (02:00, 04:00] == (02:00, 04:00) : False False
    (02:00, 04:00) == [02:00, 04:00] : False False
    (02:00, 04:00) == [02:00, 04:00) : False False
    (02:00, 04:00) == (02:00, 04:00] : False False
    (02:00, 04:00) == (02:00, 04:00) : True True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [02:00, 04:00] == [02:00, 05:00] : False False
    [02:00, 04:00] == [02:00, 05:00) : True True
    [02:00, 04:00] == (02:00, 05:00] : False False
    [02:00, 04:00] == (02:00, 05:00) : False False
    [02:00, 04:00) == [02:00, 05:00] : False False
    [02:00, 04:00) == [02:00, 05:00) : False False
    [02:00, 04:00) == (02:00, 05:00] : False False
    [02:00, 04:00) == (02:00, 05:00) : False False
    (02:00, 04:00] == [02:00, 05:00] : False False
    (02:00, 04:00] == [02:00, 05:00) : False False
    (02:00, 04:00] == (02:00, 05:00] : False False
    (02:00, 04:00] == (02:00, 05:00) : True True
    (02:00, 04:00) == [02:00, 05:00] : False False
    (02:00, 04:00) == [02:00, 05:00) : False False
    (02:00, 04:00) == (02:00, 05:00] : False False
    (02:00, 04:00) == (02:00, 05:00) : False False

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print \
    ...             ( "%s < %s : %5s; %s <= %s : %s"
    ...             % (r1, r2, r1 < r2, r1, r2, r1 <= r2)
    ...             )
    [02:00, 04:00] < [02:00, 05:00] :  True; [02:00, 04:00] <= [02:00, 05:00] : True
    [02:00, 04:00] < [02:00, 05:00) : False; [02:00, 04:00] <= [02:00, 05:00) : True
    [02:00, 04:00] < (02:00, 05:00] :  True; [02:00, 04:00] <= (02:00, 05:00] : True
    [02:00, 04:00] < (02:00, 05:00) :  True; [02:00, 04:00] <= (02:00, 05:00) : True
    [02:00, 04:00) < [02:00, 05:00] :  True; [02:00, 04:00) <= [02:00, 05:00] : True
    [02:00, 04:00) < [02:00, 05:00) :  True; [02:00, 04:00) <= [02:00, 05:00) : True
    [02:00, 04:00) < (02:00, 05:00] :  True; [02:00, 04:00) <= (02:00, 05:00] : True
    [02:00, 04:00) < (02:00, 05:00) :  True; [02:00, 04:00) <= (02:00, 05:00) : True
    (02:00, 04:00] < [02:00, 05:00] : False; (02:00, 04:00] <= [02:00, 05:00] : False
    (02:00, 04:00] < [02:00, 05:00) : False; (02:00, 04:00] <= [02:00, 05:00) : False
    (02:00, 04:00] < (02:00, 05:00] :  True; (02:00, 04:00] <= (02:00, 05:00] : True
    (02:00, 04:00] < (02:00, 05:00) : False; (02:00, 04:00] <= (02:00, 05:00) : True
    (02:00, 04:00) < [02:00, 05:00] : False; (02:00, 04:00) <= [02:00, 05:00] : False
    (02:00, 04:00) < [02:00, 05:00) : False; (02:00, 04:00) <= [02:00, 05:00) : False
    (02:00, 04:00) < (02:00, 05:00] :  True; (02:00, 04:00) <= (02:00, 05:00] : True
    (02:00, 04:00) < (02:00, 05:00) :  True; (02:00, 04:00) <= (02:00, 05:00) : True

    >>> for r1 in (ii_25, ix_25, xi_25, xx_25) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print \
    ...             ( "%s > %s : %5s; %s >= %s : %s"
    ...             % (r1, r2, r1 > r2, r1, r2, r1 >= r2)
    ...             )
    [02:00, 05:00] > [02:00, 04:00] :  True; [02:00, 05:00] >= [02:00, 04:00] : True
    [02:00, 05:00] > [02:00, 04:00) :  True; [02:00, 05:00] >= [02:00, 04:00) : True
    [02:00, 05:00] > (02:00, 04:00] : False; [02:00, 05:00] >= (02:00, 04:00] : False
    [02:00, 05:00] > (02:00, 04:00) : False; [02:00, 05:00] >= (02:00, 04:00) : False
    [02:00, 05:00) > [02:00, 04:00] : False; [02:00, 05:00) >= [02:00, 04:00] : True
    [02:00, 05:00) > [02:00, 04:00) :  True; [02:00, 05:00) >= [02:00, 04:00) : True
    [02:00, 05:00) > (02:00, 04:00] : False; [02:00, 05:00) >= (02:00, 04:00] : False
    [02:00, 05:00) > (02:00, 04:00) : False; [02:00, 05:00) >= (02:00, 04:00) : False
    (02:00, 05:00] > [02:00, 04:00] :  True; (02:00, 05:00] >= [02:00, 04:00] : True
    (02:00, 05:00] > [02:00, 04:00) :  True; (02:00, 05:00] >= [02:00, 04:00) : True
    (02:00, 05:00] > (02:00, 04:00] :  True; (02:00, 05:00] >= (02:00, 04:00] : True
    (02:00, 05:00] > (02:00, 04:00) :  True; (02:00, 05:00] >= (02:00, 04:00) : True
    (02:00, 05:00) > [02:00, 04:00] :  True; (02:00, 05:00) >= [02:00, 04:00] : True
    (02:00, 05:00) > [02:00, 04:00) :  True; (02:00, 05:00) >= [02:00, 04:00) : True
    (02:00, 05:00) > (02:00, 04:00] : False; (02:00, 05:00) >= (02:00, 04:00] : True
    (02:00, 05:00) > (02:00, 04:00) :  True; (02:00, 05:00) >= (02:00, 04:00) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "in", r2, ":", r1 in r2)
    [02:00, 04:00] in [02:00, 04:00] : True
    [02:00, 04:00] in [02:00, 04:00) : False
    [02:00, 04:00] in (02:00, 04:00] : False
    [02:00, 04:00] in (02:00, 04:00) : False
    [02:00, 04:00) in [02:00, 04:00] : True
    [02:00, 04:00) in [02:00, 04:00) : True
    [02:00, 04:00) in (02:00, 04:00] : False
    [02:00, 04:00) in (02:00, 04:00) : False
    (02:00, 04:00] in [02:00, 04:00] : True
    (02:00, 04:00] in [02:00, 04:00) : False
    (02:00, 04:00] in (02:00, 04:00] : True
    (02:00, 04:00] in (02:00, 04:00) : False
    (02:00, 04:00) in [02:00, 04:00] : True
    (02:00, 04:00) in [02:00, 04:00) : True
    (02:00, 04:00) in (02:00, 04:00] : True
    (02:00, 04:00) in (02:00, 04:00) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "in", r2, ":", r1 in r2, "<->", r2 in r1)
    [02:00, 04:00] in [02:00, 05:00] : True <-> False
    [02:00, 04:00] in [02:00, 05:00) : True <-> True
    [02:00, 04:00] in (02:00, 05:00] : False <-> False
    [02:00, 04:00] in (02:00, 05:00) : False <-> True
    [02:00, 04:00) in [02:00, 05:00] : True <-> False
    [02:00, 04:00) in [02:00, 05:00) : True <-> False
    [02:00, 04:00) in (02:00, 05:00] : False <-> False
    [02:00, 04:00) in (02:00, 05:00) : False <-> False
    (02:00, 04:00] in [02:00, 05:00] : True <-> False
    (02:00, 04:00] in [02:00, 05:00) : True <-> False
    (02:00, 04:00] in (02:00, 05:00] : True <-> False
    (02:00, 04:00] in (02:00, 05:00) : True <-> True
    (02:00, 04:00) in [02:00, 05:00] : True <-> False
    (02:00, 04:00) in [02:00, 05:00) : True <-> False
    (02:00, 04:00) in (02:00, 05:00] : True <-> False
    (02:00, 04:00) in (02:00, 05:00) : True <-> False

    >>> for i in range (1, 4) :
    ...     for bs in ("[]", "[)", "(]", "()") :
    ...         r = R (dtt (1), dtt (i), bs)
    ...         print \
    ...             ( "r : %s %5s; 1 in r: %5s; 2 in r: %5s"
    ...             % (r, bool (r), dtt (1) in r, dtt (2) in r)
    ...             )
    r : [01:00, 01:00]  True; 1 in r:  True; 2 in r: False
    r : [01:00, 01:00) False; 1 in r: False; 2 in r: False
    r : (01:00, 01:00] False; 1 in r: False; 2 in r: False
    r : (01:00, 01:00) False; 1 in r: False; 2 in r: False
    r : [01:00, 02:00]  True; 1 in r:  True; 2 in r:  True
    r : [01:00, 02:00)  True; 1 in r:  True; 2 in r: False
    r : (01:00, 02:00]  True; 1 in r: False; 2 in r:  True
    r : (01:00, 02:00) False; 1 in r: False; 2 in r: False
    r : [01:00, 03:00]  True; 1 in r:  True; 2 in r:  True
    r : [01:00, 03:00)  True; 1 in r:  True; 2 in r:  True
    r : (01:00, 03:00]  True; 1 in r: False; 2 in r:  True
    r : (01:00, 03:00)  True; 1 in r: False; 2 in r:  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ab (R (dtt (2), dtt (3), bt1), R (dtt (1), dtt (2), bt2))
    ...         _show_ab (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    ...         _show_ab (R (dtt (4), dtt (6), bt1), R (dtt (1), dtt (3), bt2))
    [02:00, 03:00] after [01:00, 02:00] : False
    [03:00, 05:00] after [01:00, 03:00] : False
    [04:00, 06:00] after [01:00, 03:00] :  True
    [02:00, 03:00] after [01:00, 02:00) :  True
    [03:00, 05:00] after [01:00, 03:00) :  True
    [04:00, 06:00] after [01:00, 03:00) :  True
    [02:00, 03:00] after (01:00, 02:00] : False
    [03:00, 05:00] after (01:00, 03:00] : False
    [04:00, 06:00] after (01:00, 03:00] :  True
    [02:00, 03:00] after (01:00, 02:00) : False
    [03:00, 05:00] after (01:00, 03:00) :  True
    [04:00, 06:00] after (01:00, 03:00) :  True
    [02:00, 03:00) after [01:00, 02:00] : False
    [03:00, 05:00) after [01:00, 03:00] : False
    [04:00, 06:00) after [01:00, 03:00] :  True
    [02:00, 03:00) after [01:00, 02:00) :  True
    [03:00, 05:00) after [01:00, 03:00) :  True
    [04:00, 06:00) after [01:00, 03:00) :  True
    [02:00, 03:00) after (01:00, 02:00] : False
    [03:00, 05:00) after (01:00, 03:00] : False
    [04:00, 06:00) after (01:00, 03:00] :  True
    [02:00, 03:00) after (01:00, 02:00) : False
    [03:00, 05:00) after (01:00, 03:00) :  True
    [04:00, 06:00) after (01:00, 03:00) :  True
    (02:00, 03:00] after [01:00, 02:00] :  True
    (03:00, 05:00] after [01:00, 03:00] :  True
    (04:00, 06:00] after [01:00, 03:00] :  True
    (02:00, 03:00] after [01:00, 02:00) :  True
    (03:00, 05:00] after [01:00, 03:00) :  True
    (04:00, 06:00] after [01:00, 03:00) :  True
    (02:00, 03:00] after (01:00, 02:00] :  True
    (03:00, 05:00] after (01:00, 03:00] :  True
    (04:00, 06:00] after (01:00, 03:00] :  True
    (02:00, 03:00] after (01:00, 02:00) : False
    (03:00, 05:00] after (01:00, 03:00) :  True
    (04:00, 06:00] after (01:00, 03:00) :  True
    (02:00, 03:00) after [01:00, 02:00] : False
    (03:00, 05:00) after [01:00, 03:00] :  True
    (04:00, 06:00) after [01:00, 03:00] :  True
    (02:00, 03:00) after [01:00, 02:00) : False
    (03:00, 05:00) after [01:00, 03:00) :  True
    (04:00, 06:00) after [01:00, 03:00) :  True
    (02:00, 03:00) after (01:00, 02:00] : False
    (03:00, 05:00) after (01:00, 03:00] :  True
    (04:00, 06:00) after (01:00, 03:00] :  True
    (02:00, 03:00) after (01:00, 02:00) : False
    (03:00, 05:00) after (01:00, 03:00) :  True
    (04:00, 06:00) after (01:00, 03:00) :  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_adj (R (dtt (2), dtt (3), bt1), R (dtt (1), dtt (2), bt2))
    ...         _show_adj (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    ...         _show_adj (R (dtt (4), dtt (6), bt1), R (dtt (1), dtt (3), bt2))
    [02:00, 03:00] is_adjacent [01:00, 02:00] : False
    [03:00, 05:00] is_adjacent [01:00, 03:00] : False
    [04:00, 06:00] is_adjacent [01:00, 03:00] :  True
    [02:00, 03:00] is_adjacent [01:00, 02:00) :  True
    [03:00, 05:00] is_adjacent [01:00, 03:00) :  True
    [04:00, 06:00] is_adjacent [01:00, 03:00) : False
    [02:00, 03:00] is_adjacent (01:00, 02:00] : False
    [03:00, 05:00] is_adjacent (01:00, 03:00] : False
    [04:00, 06:00] is_adjacent (01:00, 03:00] :  True
    [02:00, 03:00] is_adjacent (01:00, 02:00) : False
    [03:00, 05:00] is_adjacent (01:00, 03:00) :  True
    [04:00, 06:00] is_adjacent (01:00, 03:00) : False
    [02:00, 03:00) is_adjacent [01:00, 02:00] : False
    [03:00, 05:00) is_adjacent [01:00, 03:00] : False
    [04:00, 06:00) is_adjacent [01:00, 03:00] :  True
    [02:00, 03:00) is_adjacent [01:00, 02:00) :  True
    [03:00, 05:00) is_adjacent [01:00, 03:00) :  True
    [04:00, 06:00) is_adjacent [01:00, 03:00) : False
    [02:00, 03:00) is_adjacent (01:00, 02:00] : False
    [03:00, 05:00) is_adjacent (01:00, 03:00] : False
    [04:00, 06:00) is_adjacent (01:00, 03:00] :  True
    [02:00, 03:00) is_adjacent (01:00, 02:00) : False
    [03:00, 05:00) is_adjacent (01:00, 03:00) :  True
    [04:00, 06:00) is_adjacent (01:00, 03:00) : False
    (02:00, 03:00] is_adjacent [01:00, 02:00] :  True
    (03:00, 05:00] is_adjacent [01:00, 03:00] :  True
    (04:00, 06:00] is_adjacent [01:00, 03:00] : False
    (02:00, 03:00] is_adjacent [01:00, 02:00) : False
    (03:00, 05:00] is_adjacent [01:00, 03:00) : False
    (04:00, 06:00] is_adjacent [01:00, 03:00) : False
    (02:00, 03:00] is_adjacent (01:00, 02:00] :  True
    (03:00, 05:00] is_adjacent (01:00, 03:00] :  True
    (04:00, 06:00] is_adjacent (01:00, 03:00] : False
    (02:00, 03:00] is_adjacent (01:00, 02:00) : False
    (03:00, 05:00] is_adjacent (01:00, 03:00) : False
    (04:00, 06:00] is_adjacent (01:00, 03:00) : False
    (02:00, 03:00) is_adjacent [01:00, 02:00] : False
    (03:00, 05:00) is_adjacent [01:00, 03:00] :  True
    (04:00, 06:00) is_adjacent [01:00, 03:00] : False
    (02:00, 03:00) is_adjacent [01:00, 02:00) : False
    (03:00, 05:00) is_adjacent [01:00, 03:00) : False
    (04:00, 06:00) is_adjacent [01:00, 03:00) : False
    (02:00, 03:00) is_adjacent (01:00, 02:00] : False
    (03:00, 05:00) is_adjacent (01:00, 03:00] :  True
    (04:00, 06:00) is_adjacent (01:00, 03:00] : False
    (02:00, 03:00) is_adjacent (01:00, 02:00) : False
    (03:00, 05:00) is_adjacent (01:00, 03:00) : False
    (04:00, 06:00) is_adjacent (01:00, 03:00) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    [03:00, 05:00] overlaps [01:00, 03:00] :  True
    [03:00, 05:00] overlaps [01:00, 03:00) : False
    [03:00, 05:00] overlaps (01:00, 03:00] :  True
    [03:00, 05:00] overlaps (01:00, 03:00) : False
    [03:00, 05:00) overlaps [01:00, 03:00] :  True
    [03:00, 05:00) overlaps [01:00, 03:00) : False
    [03:00, 05:00) overlaps (01:00, 03:00] :  True
    [03:00, 05:00) overlaps (01:00, 03:00) : False
    (03:00, 05:00] overlaps [01:00, 03:00] : False
    (03:00, 05:00] overlaps [01:00, 03:00) : False
    (03:00, 05:00] overlaps (01:00, 03:00] : False
    (03:00, 05:00] overlaps (01:00, 03:00) : False
    (03:00, 05:00) overlaps [01:00, 03:00] : False
    (03:00, 05:00) overlaps [01:00, 03:00) : False
    (03:00, 05:00) overlaps (01:00, 03:00] : False
    (03:00, 05:00) overlaps (01:00, 03:00) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (4), bt2))
    [03:00, 05:00] overlaps [01:00, 04:00] :  True
    [03:00, 05:00] overlaps [01:00, 04:00) :  True
    [03:00, 05:00] overlaps (01:00, 04:00] :  True
    [03:00, 05:00] overlaps (01:00, 04:00) :  True
    [03:00, 05:00) overlaps [01:00, 04:00] :  True
    [03:00, 05:00) overlaps [01:00, 04:00) :  True
    [03:00, 05:00) overlaps (01:00, 04:00] :  True
    [03:00, 05:00) overlaps (01:00, 04:00) :  True
    (03:00, 05:00] overlaps [01:00, 04:00] :  True
    (03:00, 05:00] overlaps [01:00, 04:00) : False
    (03:00, 05:00] overlaps (01:00, 04:00] :  True
    (03:00, 05:00] overlaps (01:00, 04:00) : False
    (03:00, 05:00) overlaps [01:00, 04:00] :  True
    (03:00, 05:00) overlaps [01:00, 04:00) : False
    (03:00, 05:00) overlaps (01:00, 04:00] :  True
    (03:00, 05:00) overlaps (01:00, 04:00) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    [03:00, 05:00] intersection [01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00] intersection [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00] intersection (01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00] intersection (01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) intersection [01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00) intersection [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) intersection (01:00, 03:00] : [03:00, 03:00]
    [03:00, 05:00) intersection (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] intersection [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] intersection [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] intersection (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] intersection (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) intersection [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) intersection [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) intersection (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) intersection (01:00, 03:00) : (03:00, 03:00)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (4), bt2))
    [03:00, 05:00] intersection [01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00] intersection [01:00, 04:00) : [03:00, 03:00]
    [03:00, 05:00] intersection (01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00] intersection (01:00, 04:00) : [03:00, 03:00]
    [03:00, 05:00) intersection [01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00) intersection [01:00, 04:00) : [03:00, 03:00]
    [03:00, 05:00) intersection (01:00, 04:00] : [03:00, 04:00]
    [03:00, 05:00) intersection (01:00, 04:00) : [03:00, 03:00]
    (03:00, 05:00] intersection [01:00, 04:00] : [04:00, 04:00]
    (03:00, 05:00] intersection [01:00, 04:00) : (04:00, 03:00)
    (03:00, 05:00] intersection (01:00, 04:00] : [04:00, 04:00]
    (03:00, 05:00] intersection (01:00, 04:00) : (04:00, 03:00)
    (03:00, 05:00) intersection [01:00, 04:00] : [04:00, 04:00]
    (03:00, 05:00) intersection [01:00, 04:00) : (04:00, 03:00)
    (03:00, 05:00) intersection (01:00, 04:00] : [04:00, 04:00]
    (03:00, 05:00) intersection (01:00, 04:00) : (04:00, 03:00)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (3), bt2))
    [03:00, 05:00] union [01:00, 03:00] : [01:00, 05:00]
    [03:00, 05:00] union [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00] union (01:00, 03:00] : (01:00, 05:00]
    [03:00, 05:00] union (01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) union [01:00, 03:00] : [01:00, 05:00)
    [03:00, 05:00) union [01:00, 03:00) : (03:00, 03:00)
    [03:00, 05:00) union (01:00, 03:00] : (01:00, 05:00)
    [03:00, 05:00) union (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] union [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] union [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00] union (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00] union (01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) union [01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) union [01:00, 03:00) : (03:00, 03:00)
    (03:00, 05:00) union (01:00, 03:00] : (03:00, 03:00)
    (03:00, 05:00) union (01:00, 03:00) : (03:00, 03:00)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (dtt (3), dtt (5), bt1), R (dtt (1), dtt (4), bt2))
    [03:00, 05:00] union [01:00, 04:00] : [01:00, 05:00]
    [03:00, 05:00] union [01:00, 04:00) : [01:00, 05:00]
    [03:00, 05:00] union (01:00, 04:00] : (01:00, 05:00]
    [03:00, 05:00] union (01:00, 04:00) : (01:00, 05:00]
    [03:00, 05:00) union [01:00, 04:00] : [01:00, 04:00]
    [03:00, 05:00) union [01:00, 04:00) : [01:00, 05:00)
    [03:00, 05:00) union (01:00, 04:00] : (01:00, 04:00]
    [03:00, 05:00) union (01:00, 04:00) : (01:00, 05:00)
    (03:00, 05:00] union [01:00, 04:00] : [01:00, 05:00]
    (03:00, 05:00] union [01:00, 04:00) : (04:00, 03:00)
    (03:00, 05:00] union (01:00, 04:00] : (01:00, 05:00]
    (03:00, 05:00] union (01:00, 04:00) : (04:00, 03:00)
    (03:00, 05:00) union [01:00, 04:00] : [01:00, 04:00]
    (03:00, 05:00) union [01:00, 04:00) : (04:00, 03:00)
    (03:00, 05:00) union (01:00, 04:00] : (01:00, 04:00]
    (03:00, 05:00) union (01:00, 04:00) : (04:00, 03:00)

    >>> for bt in ("  ", "[]", "[)", "(]", "()") :
    ...     s = " ".join ((bt [0], "02:00, 05:00:00", bt[1]))
    ...     _show_fs (R, s)
      02:00, 05:00:00   : Time_Range_H (datetime.time(2, 0), datetime.time(5, 0), '[)')
    [ 02:00, 05:00:00 ] : Time_Range_H (datetime.time(2, 0), datetime.time(5, 0), '[]')
    [ 02:00, 05:00:00 ) : Time_Range_H (datetime.time(2, 0), datetime.time(5, 0), '[)')
    ( 02:00, 05:00:00 ] : Time_Range_H (datetime.time(2, 0), datetime.time(5, 0), '(]')
    ( 02:00, 05:00:00 ) : Time_Range_H (datetime.time(2, 0), datetime.time(5, 0), '()')

""" ### _test_time_range_h

__test__ = dict \
    ( test_date_range   = _test_date_range
    , test_time_range   = _test_time_range
    , test_time_range_h = _test_time_range_h
    )

__sphinx__members = TFL._.Range._sphinx_members (globals ())

if __name__ != "__main__" :
    CAL._Export ("*")
### __END__ CAL.Range_DT
