# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.SRM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SRM.Attr_Type
#
# Purpose
#    Define attribute types for package GTW.OMP.SRM
#
# Revision Dates
#    15-Apr-2010 (CT) Creation
#    28-Apr-2010 (CT) `Race_Result.ui_display_format` redefined
#    11-May-2010 (CT) `A_Regatta_Result` added
#    12-May-2010 (CT) `A_Nation.Table` filled with `unicode` instead of `str`
#     6-Sep-2010 (CT) `Race_Result` removed (now implemented as `Link1`)
#    13-Oct-2010 (CT) `example` added
#    22-Sep-2011 (CT) s/C_Type/P_Type/ for _A_Composite_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    11-May-2012 (CT) Add `RSA` to `A_Nation`
#    14-May-2012 (CT) Add `A_Nation.P_Type`
#     7-Aug-2012 (CT) Add `example` to attributes of `Regatta_Result`
#     8-Sep-2012 (CT) Derive `A_Nation` from `A_Enum`, not `_A_Named_Object_`
#     8-Sep-2012 (CT) Redefine `A_Nation.cooked` to call `upper`
#    24-Jan-2013 (CT) Add guard around `upper` to `A_Nation.cooked`
#    ««revision-date»»···
#--

from   __future__               import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *
from   _MOM.import_MOM          import _A_Composite_, _A_Named_Object_

import _GTW._OMP._SRM

from   _TFL.I18N                import _, _T, _Tn

class A_Nation (A_Enum) :
    """Nation a boat or sailor sails for."""

    ### http://en.wikipedia.org/wiki/List_of_IOC_country_codes

    example    = "AUT"
    typ        = "Nation"

    C_Type     = A_String
    max_length = 3

    Table      = \
        { "AUS" :  _("Australia")
        , "AUT" :  _("Austria")
        , "BEL" :  _("Belgium")
        , "CAN" :  _("Canada")
        , "CRO" :  _("Croatia")
        , "CYP" :  _("Cyprus")
        , "CZE" :  _("Czech Republic")
        , "DEN" :  _("Denmark")
        , "ESP" :  _("Spain")
        , "EST" :  _("Estonia")
        , "FIN" :  _("Finland")
        , "FRA" :  _("France")
        , "GBR" :  _("Great Britain")
        , "GER" :  _("Germany")
        , "GRE" :  _("Greece")
        , "HUN" :  _("Hungary")
        , "IRL" :  _("Ireland")
        , "ISL" :  _("Iceland")
        , "ITA" :  _("Italy")
        , "LAT" :  _("Latvia")
        , "LIE" :  _("Lichtenstein")
        , "LTU" :  _("Lithuania")
        , "LUX" :  _("Luxembourg")
        , "MLT" :  _("Malta")
        , "MNE" :  _("Montenegro")
        , "MON" :  _("Monaco")
        , "NED" :  _("Netherlands")
        , "NOR" :  _("Norway")
        , "NZL" :  _("New Zealand")
        , "POL" :  _("Poland")
        , "POR" :  _("Portugal")
        , "ROU" :  _("Romania")
        , "RSA" :  _("South Africa")
        , "RUS" :  _("Russia")
        , "SLO" :  _("Slovenia")
        , "SRB" :  _("Serbia")
        , "SUI" :  _("Switzerland")
        , "SVK" :  _("Slovakia")
        , "SWE" :  _("Sweden")
        , "UKR" :  _("Ukraine")
        , "USA" :  _(u"United States")
        }

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if value :
            try :
                v = value.upper ()
            except Exception as exc :
                raise ValueError \
                    ( "Value for %s must be string, got %s %r"
                    % (soc, type (value), value)
                    )
            else :
                return super (A_Nation, soc).cooked (v)
    # end def cooked

# end class A_Nation

_Ancestor_Essence = MOM.An_Entity

class Regatta_Result (_Ancestor_Essence) :
    """Provide information about the result of a regatta."""

    PNS = GTW.OMP.SRM

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class date (A_Date_Time) :
            """Date of regatta result."""

            kind               = Attr.Necessary
            example            = "1979-08-18"

        # end class date

        class software (A_String) :
            """Name of software used for managing the regatta."""

            kind               = Attr.Optional
            example            = "Blowing Bits Inc."

        # end class software

        class status (A_String) :
            """Status of result (e.g., `preliminary` or `final`)."""

            kind               = Attr.Optional
            example            = "Final"

        # end class status

    # end class _Attributes

# end class Regatta_Result

class A_Regatta_Result (_A_Composite_) :
    """Information about a regatta's result."""

    P_Type          = Regatta_Result
    typ             = "Regatta_Result"

# end class A_Regatta_Result

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Attr_Type
