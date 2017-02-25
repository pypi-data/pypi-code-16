# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.NET.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.NET.Attr_Type
#
# Purpose
#    Define attribute types for package GTW.OMP.NET
#
# Revision Dates
#     6-Mar-2012 (CT) Creation
#    22-May-2012 (RS) Add `A_IP6_Address`, `A_IP6_Network` and common
#                     ancestor `A_IP_Address`, extend syntax checks
#    23-May-2012 (RS) Rename `A_IP_Address` -> `_A_IP_Address_`
#    23-May-2012 (RS) Add `_syntax_re` for `_A_IP_Address_`
#    10-Aug-2012 (RS) Make all IP-related types decendants of `_A_Composite_`
#    11-Aug-2012 (MG) Preparation for special SAS query functions
#    13-Aug-2012 (RS) Add `mask_len` to `IP4_Network` and `IP6_Network`,
#                     create common ancestor of all composite ip types
#    23-Sep-2012 (RS) Use `rsclib.IP_Address` for `_A_IP_Address_`
#    24-Sep-2012 (RS) Fix/add mixins for SAS backend
#    24-Sep-2012 (CT) Raise `Attribute_Value` in `_A_IP4_Address_.check_syntax`
#    24-Sep-2012 (RS) Move `SAS` specific stuff to `SAS_Attr_Type`
#    10-Oct-2012 (CT) Add `PNS` to `IP_Address`
#    12-Oct-2012 (RS) Add `code_format`
#     5-Jun-2013 (CT) Use `is_attr_type`, not home-grown code
#    13-Jun-2013 (CT) Add `pns_alias`
#     2-Aug-2013 (CT) Use `A_Int.max_value...`, not literals
#     2-Aug-2013 (CT) Add import callback for `_GTW._OMP._NET.SAW`, `.SAW_PG`
#     6-Aug-2013 (CT) Remove composite attributes, aka, major surgery
#    11-Dec-2015 (CT) Use `attr_types_of_module`, not home-grown code
#    16-Dec-2015 (CT) Use `_Add_Import_Callback` as decorator
#    28-Apr-2016 (CT) Remove `glob`, `locl` from `from_string`, `_from_string`
#    14-Sep-2016 (CT) Attach import callback to "_MOM._DBW._SAW.Attr"
#                     - not "_MOM._DBW._SAW.Manager"
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, unicode_literals

from   _MOM.import_MOM       import *
from   _MOM.import_MOM       import _A_Composite_, _A_String_

from   _GTW                  import GTW

from   _TFL.pyk              import pyk
from   _TFL.I18N             import _
from   _TFL.Regexp           import Regexp, re

from   rsclib.IP_Address     import IP_Address  as R_IP_Address
from   rsclib.IP_Address     import IP4_Address as R_IP4_Address
from   rsclib.IP_Address     import IP6_Address as R_IP6_Address

import _GTW._OMP._NET

import _TFL.Sorted_By

class _A_CIDR_ (A_Attr_Type) :
    """Model abstract address of IP network."""

    P_Type      = R_IP_Address
    code_format = '"%r"' # rsclib.IP_Address formats without quotes

    class Pickler (TFL.Meta.Object) :

        @classmethod
        def as_cargo (cls, attr_kind, attr_type, value) :
            if value is not None :
                return str (value)
        # end def as_cargo

        @classmethod
        def from_cargo (cls, scope, attr_kind, attr_type, cargo) :
            if cargo is not None :
                return attr_type.P_Type (cargo)
        # end def from_cargo

    # end class Pickler

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, value, obj = None) :
        if value :
            # this may raise a ValueError
            return soc.P_Type (value)
    # end def _from_string

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if isinstance (value, pyk.string_types) :
            value = soc.P_Type (value)
        if not isinstance (value, R_IP_Address) :
            raise TypeError ("Invalid type for cooked : got %r" % (value, ))
        return value
    # end def cooked

# end class _A_CIDR_

class _A_IP_Address_ (_A_CIDR_) :

    def check_syntax (self, obj, val) :
        if val and val.mask != self.P_Type.bitlen :
            raise MOM.Error.Attribute_Value \
                ( obj, self.name, val, self.kind
                , ValueError
                    ( "Invalid netmask: %s; must be empty or %s"
                    % (val.mask, self.P_Type.bitlen)
                    )
                )
    # end def check_syntax

# end class _A_IP_Address_

class A_IP4_Address (_A_IP_Address_) :
    """Models an address in a IP4 network."""

    P_Type            = R_IP4_Address
    example           = "192.168.42.137"
    typ               = "IP4-address"
    max_length        = 15
    syntax            = _ \
        ( "IP4 address must contain 4 decimal octets separated by `.`."
        )

# end class A_IP4_Address

class A_IP4_Network (_A_CIDR_) :
    """Model a IP4 network in CIDRR notation."""

    P_Type            = R_IP4_Address
    _adr_type         = A_IP4_Address
    _mask_len         = len (str (P_Type.bitlen))
    example           = "192.168.42.0/28"
    typ               = "IP4-network"
    max_length        = _adr_type.max_length + _mask_len + 1
    syntax            = _ \
        ( "IP4 network must contain 4 decimal octets separated by `.`, "
          "optionally followed by `/` and a number between 0 and 32."
          " The bits right of the netmask are automatically set to zero."
        )

# end class A_IP4_Network

class A_IP6_Address (_A_IP_Address_) :
    """Models an address in a IP6 network."""

    P_Type            = R_IP6_Address
    example           = "2001:db8:85a3::8a2e:370:7334"
    typ               = "IP6-address"
    max_length        = 39
    syntax            = _ \
        ( "IP6 address must contain up to 8 hexadecimal "
          "numbers with up to 4 digits separated by `:`. "
          "A single empty group `::` can be used."
        )

# end class A_IP6_Address

class A_IP6_Network (_A_CIDR_) :
    """Model a IP6 network in CIDRR notation."""

    P_Type            = R_IP6_Address
    _adr_type         = A_IP6_Address
    _mask_len         = len (str (P_Type.bitlen))
    example           = "2001:db8::/32"
    typ               = "IP6-network"
    max_length        = _adr_type.max_length + _mask_len + 1
    syntax            = _ \
        ( "IP6 network must contain up to 8 hexadecimal "
          "numbers with up to 4 digits separated by `:`. "
          "A single empty group `::` can be used."
          " This is optionally followed by `/` and a number between 0 and 128."
          " The bits right of the netmask are automatically set to zero."
        )

# end class A_IP6_Network

class A_MAC_Address (Syntax_Re_Mixin, A_String) :
    """Model a MAC address."""

    example           = "00:18:71:69:0b:c8"
    typ               = "MAC-address"
    max_length        = 17
    P_Type            = str
    syntax            = _ \
        ( "A MAC address must contain 6 hexadecimal octets separated by `:`."
        )

    _syntax_re        = Regexp \
        ( r"^"
          r"(?: [0-9A-F]{2} :){5} [0-9A-F]{2}"
          r"$"
        , re.VERBOSE | re.IGNORECASE
        )

# end class A_MAC_Address

__attr_types      = Attr.attr_types_of_module ()
__sphinx__members = __attr_types

if __name__ != "__main__" :
    GTW.OMP.NET._Export (* __attr_types)

    @GTW._Add_Import_Callback ("_MOM._DBW._SAW.Attr")
    def _import_saw (module) :
        import _GTW._OMP._NET.SAW
    # end def _import_saw

    @GTW._Add_Import_Callback ("_MOM._DBW._SAW._PG.Attr")
    def _import_saw_pg (module) :
        import _GTW._OMP._NET.SAW_PG
    # end def _import_saw_pg
### __END__ GTW.OMP.NET.Attr_Type
