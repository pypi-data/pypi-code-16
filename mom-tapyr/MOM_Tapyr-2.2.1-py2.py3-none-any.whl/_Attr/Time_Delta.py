# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Attr.Time_Delta
#
# Purpose
#    Attribute holding a Time-Delta
#
# Revision Dates
#     7-Feb-2016 (CT) Creation
#     8-Feb-2016 (CT) Add guard for `None` to `cooked`,
#                     unpack `CAL.Time_Delta` value
#     8-Feb-2016 (CT) Add test
#    28-Apr-2016 (CT) Remove `glob`, `locl` from `from_string`, `_from_string`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                        import CAL

from   _MOM.import_MOM             import *

from   _TFL.I18N                   import _, _T, _Tn
from   _TFL.pyk                    import pyk

import _CAL.Delta
import datetime

class A_Time_Delta (A_Attr_Type) :
    """Time delta value."""

    example        = "1 h"
    completer      = MOM.Attr.Completer_Spec  (0)
    typ            = _ ("Time-Delta")
    P_Type         = datetime.timedelta
    Pickler        = Pickler_As_String
    syntax         = _ \
        ( "hh:mm:ss, the seconds `ss` are optional\n"
          "One can also use values like::\n"
          "    30m"
          "    20 minutes"
          "    1.5h10.25m7.125s"
          "    1.5 hours 10.25 minutes 7.125 seconds"
          "    1.5 hours, 10.25 minutes, 7.125 seconds"
        )

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if value is not None :
            msg = "%s expected, got %r" % (soc.typ, value)
            if isinstance (value, pyk.string_types) :
                try :
                    value = CAL.Time_Delta.from_string (value)._body
                except ValueError :
                    raise MOM.Error.Attribute_Syntax (None, soc, value, msg)
            elif not isinstance (value, (datetime.timedelta)) :
                raise TypeError (msg)
            return value
    # end def cooked

    @TFL.Meta.Class_and_Instance_Method
    def as_string (soc, value) :
        result = ""
        if value is not None :
            result = pyk.text_type (value)
            if result.endswith (":00") :
                result = result [:-3]
        return result
    # end def as_string

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, s, obj = None) :
        s = s.strip ()
        if s :
            return soc.cooked (s)
    # end def _from_string

# end class A_Time_Delta

__attr_types = Attr.attr_types_of_module ()
__all__      = __attr_types

__doc__ = """
     >>> a = A_Time_Delta.cooked ("1.5h10.25m7.125s")
     >>> print (A_Time_Delta.as_string (a))
     1:40:22.125000
     >>> a
     datetime.timedelta(0, 6022, 125000)

     >>> b = A_Time_Delta.cooked ("1.5h")
     >>> print (A_Time_Delta.as_string (b))
     1:30
     >>> b
     datetime.timedelta(0, 5400)

     >>> c = A_Time_Delta.cooked ("1:30")
     >>> print (A_Time_Delta.as_string (c))
     1:30
     >>> c
     datetime.timedelta(0, 5400)

"""

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)
### __END__ MOM.Attr.Time_Delta
