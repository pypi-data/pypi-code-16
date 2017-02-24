# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A--3411 Weidling, Austria. rsc@runtux.com
# ****************************************************************************
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Attr.Date_Time_Delta
#
# Purpose
#    Attribute type for date/time delta
#
# Revision Dates
#    16-Jun-2014 (RS) Creation
#    11-Jul-2014 (CT) Derive from `A_Attr_Type`, set `Pickler.Type` to `A_Float`
#    11-Dec-2015 (CT) Use `attr_types_of_module`, not home-grown code
#    28-Apr-2016 (CT) Remove `glob`, `locl` from `from_string`, `_from_string`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _CAL                  import CAL

from   _MOM.import_MOM       import *
from   _MOM.import_MOM       import _A_Float_, _A_String_

from   _TFL.I18N             import _
from   _TFL.pyk              import pyk

import _CAL.Delta

import datetime

_Ancestor_Essence = A_Attr_Type

class A_Date_Time_Delta (_Ancestor_Essence) :
    """A date/time delta."""

    code_format      = "%s"
    example          = "1w 2d 13:10:17.5"
    typ              = _ ("Time Delta")
    P_Type           = datetime.timedelta
    ui_length        = 20

    class Pickler (TFL.Meta.Object) :

        Type          = A_Float

        @classmethod
        def as_cargo (cls, attr_kind, attr_type, value) :
            if value is not None :
                return value.total_seconds () / 86400.
        # end def as_cargo

        @classmethod
        def from_cargo (cls, scope, attr_kind, attr_type, cargo) :
            if cargo is not None :
                return datetime.timedelta (days = float (cargo))
        # end def from_cargo

    # end class Pickler

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if isinstance (value, pyk.string_types) :
            try :
                value = soc._from_string (value)
            except MOM.Error.Attribute_Syntax :
                raise
        elif not isinstance (value, datetime.timedelta) :
            raise TypeError ("Date-or-delta expected, got %r" % (value,))
        return value
    #end def cooked

    @TFL.Meta.Class_and_Instance_Method
    def as_string (soc, value) :
        if value is not None :
            if isinstance (value, datetime.timedelta) :
                r = []
                if value.days :
                    r.append ("%sd" % value.days)
                if value.seconds or value.microseconds :
                    if r :
                        r.append (" ")
                    r.append ("%02d:" % (value.seconds // 3600))
                    r.append ("%02d:" % ((value.seconds % 3600) // 60))
                    r.append ("%02d"  % (value.seconds % 60))
                if value.microseconds :
                    r.append (".%06d" % value.microseconds)
                return "".join (r)
            else :
                return pyk.text_type (value)
        return ""
    # end def as_string

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, in_s, obj = None) :
        s = in_s.strip ()
        if s :
            dtd = CAL.Date_Time_Delta.from_string (s)
            return datetime.timedelta \
                ( days         = dtd.days
                , seconds      = dtd.seconds
                , microseconds = dtd.microseconds
                )
    # end def _from_string

# end class A_Date_Time_Delta

__attr_types      = Attr.attr_types_of_module ()
__sphinx__members = __attr_types

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)
### __END__ MOM.Attr.Date_Interval
