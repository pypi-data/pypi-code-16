# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.E164.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.E164.Polisher
#
# Purpose
#    Provide MOM Polishers for phone number attributes
#
# Revision Dates
#    30-Jul-2015 (CT) Start creation
#    31-Jul-2015 (CT) Finish creation
#     7-Oct-2015 (CT) Change `SN._polished` to not assign `strict_err` with `as`
#                     (Python 3 compatibility!)
#    26-Apr-2016 (CT) Add `buddies` to `_E164_Polisher_`
#    22-May-2016 (CT) Add guard `c_match.attr_dict.get (name)` to
#                     `SN._polished_non_strict`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _MOM                     import MOM
from   _TFL                     import TFL

from   _GTW._OMP._PAP._E164     import E164

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import \
    (Regexp, Multi_Regexp, Re_Replacer, Multi_Re_Replacer, re)

import _GTW._OMP._PAP._E164.Country
import _GTW._OMP._PAP._E164.Error

import _MOM._Attr.Polisher

class _E164_Polisher_ (MOM.Attr.Polisher._Polisher_) :

    buddies        = ("cc", "ndc", "sn")

    _cleanup_value = Multi_Re_Replacer \
        ( Re_Replacer (r"[ \t]+", " ") ### compress space, tab
        , Re_Replacer (r" +",     " ") ### compress no-break space to space
        , Re_Replacer (r" +",     "" ) ### remove narrow no-break space
        )

    def _attr_value (self, attr, name, value, value_dict, essence) :
        result = self.__super._attr_value \
            (attr, name, value, value_dict, essence)
        if result is None and name != attr.name :
            result = getattr (essence, name, None)
        if result :
            result = self._cleanup_value (result)
        return result
    # end def _attr_value

# end class _E164_Polisher_

class CC (_E164_Polisher_) :
    """Polisher for `cc` attribute."""

    def _polished (self, attr, name, value, value_dict, essence, picky) :
        result = {}
        match  = E164.Country.match (value)
        if match :
            result [name] = match.country.code
            ndc = self._attr_value (attr, "ndc", None, value_dict, essence)
            sn  = self._attr_value (attr, "sn",  None, value_dict, essence)
            if not (ndc or sn) :
                try :
                    result.update (match.attr_dict)
                except ValueError :
                    pass
        else :
            raise ValueError (_T ("Unknown country code %s") % value)
        return result
    # end def _polished

# end class CC

class NDC (_E164_Polisher_) :
    """Polisher for `ndc`, `cc` attributes."""

    def _polished (self, attr, name, value, value_dict, essence, picky) :
        cc      = self._attr_value (attr, "cc", None, value_dict, essence)
        country = None
        c_match = E164.Country.match_strict (value)
        rest    = value
        result  = {}
        if c_match :
            country       = c_match.country
            rest          = c_match.ndc_sn
            result ["cc"] = c_match.cc
        elif cc :
            country       = E164.Country (cc)
        else :
            country       = E164.Country_0
        r_match = country.regexp.match (rest)
        if r_match :
            ndc = r_match.groupdict () ["ndc"]
        else :
            raise ValueError \
                (_T ("Unknown network destination code %s") % value)
        result [name] = ndc
        return result
    # end def _polished

# end class NDC

class SN (_E164_Polisher_) :
    """Polisher for `cc`, `ndc`, `sn` attributes."""

    def _polished (self, attr, name, value, value_dict, essence, picky) :
        country    = None
        c_match    = E164.Country.match_strict (value)
        cc         = self._attr_value (attr, "cc",  None, value_dict, essence)
        ndc        = self._attr_value (attr, "ndc", None, value_dict, essence)
        result     = { name : value } ### assume `value` is OK
        call_pns   = False            ### call `_polished_non_strict` if True
        strict_err = None
        if c_match :
            result.update (c_match.attr_dict)
        else :
            if cc :
                country = E164.Country (cc)
                if ndc :
                    try :
                        result [name] = country.cleaned_sn (ndc, value)
                    except E164.SN_Too_Long as err :
                        strict_err = err
                        call_pns   = True
                else :
                    try :
                        ndc, sn = country.split (value)
                    except ValueError as err :
                        strict_err = err
                        if picky :
                            call_pns = True
                    else :
                        result.update (ndc = ndc, sn = sn)
            elif (picky and not ndc) or value.startswith ("0") :
                call_pns = True
            if call_pns :
                try :
                    result.update \
                        ( self._polished_non_strict
                            (attr, name, value, value_dict, essence, picky)
                        )
                except E164.ValueError :
                    if strict_err is not None :
                        raise strict_err
            self.strict = not call_pns
        return result
    # end def _polished

    def _polished_non_strict \
            (self, attr, name, value, value_dict, essence, picky) :
        c_match = E164.Country.match (value)
        result  = {}
        if c_match and c_match.attr_dict.get (name) :
            result.update (c_match.attr_dict)
        else :
            result = MOM.Attr.Polisher.phone_sn_split \
                (attr, value_dict, essence, picky, value)
        return result
    # end def _polished_non_strict

# end class SN

_test_fixtures_ = """
    >>> from _TFL.Record import Record

    >>> def show (v, attr, polisher, picky = False, ** kw) :
    ...     r  = polisher (attr, dict ({attr.name : v}, ** kw), picky = picky)
    ...     vs = ("%s = %s" % (k, v) for k, v in sorted (r.items ()) if v)
    ...     print (", ".join (vs))

"""

_test_cc = _test_fixtures_ + """
    >>> cc_attr     = Record (name = "cc")
    >>> cc_polisher = CC ()

    >>> show ("43", cc_attr, cc_polisher)
    cc = 43

    >>> show ("+43", cc_attr, cc_polisher)
    cc = 43

    >>> show ("0043", cc_attr, cc_polisher)
    cc = 43

    >>> show ("0", cc_attr, cc_polisher, cc = "43")
    cc = 43

    >>> with expect_except (ValueError) :
    ...     show ("+28", cc_attr, cc_polisher)
    ValueError: Unknown country code +28
"""

_test_ndc = _test_fixtures_ + """
    >>> ndc_attr     = Record (name = "ndc")
    >>> ndc_polisher = NDC ()

    >>> show ("664", ndc_attr, ndc_polisher)
    ndc = 664

    >>> show ("0664", ndc_attr, ndc_polisher)
    ndc = 664

    >>> show ("0 664", ndc_attr, ndc_polisher)
    ndc = 664

    >>> show ("664", ndc_attr, ndc_polisher, cc = "43")
    cc = 43, ndc = 664

    >>> show ("(664)", ndc_attr, ndc_polisher, cc = "43")
    cc = 43, ndc = 664

    >>> show ("+44 664", ndc_attr, ndc_polisher, cc = "43")
    cc = 44, ndc = 664

    >>> show ("+44664", ndc_attr, ndc_polisher, cc = "43")
    cc = 44, ndc = 664

    ### narrow no-break space
    >>> show ("+44 664", ndc_attr, ndc_polisher, cc = "43")
    cc = 44, ndc = 664

    >>> show ("+44 664 ", ndc_attr, ndc_polisher, cc = "43")
    cc = 44, ndc = 664

    >>> show ("+44/664", ndc_attr, ndc_polisher, cc = "43")
    cc = 44, ndc = 664

    >>> show ("+44/664/", ndc_attr, ndc_polisher, cc = "43")
    cc = 44, ndc = 664

    >>> show ("+44 (664)", ndc_attr, ndc_polisher, cc = "43")
    cc = 44, ndc = 664

    >>> with expect_except (ValueError) :
    ...     show ("+44", ndc_attr, ndc_polisher, cc = "43")
    ValueError: Unknown network destination code +44

    >>> with expect_except (ValueError) :
    ...     show ("0", ndc_attr, ndc_polisher, cc = "43")
    ValueError: Unknown network destination code 0

"""

_test_sn = _test_fixtures_ + """
    >>> sn_attr     = Record (name = "sn")
    >>> sn_polisher = SN ()

    >>> show ("43 66412345678", sn_attr, sn_polisher, cc = "43")
    cc = 43, sn = 43 66412345678

    >>> show ("43 66412345678", sn_attr, sn_polisher, cc = "43", picky = True)
    cc = 43, ndc = 664, sn = 12345678

    >>> with expect_except (ValueError) :
    ...     show ("43 43 66412345678", sn_attr, sn_polisher, cc = "43", picky = True)
    ValueError: Not a proper phone number for Country (43) [Austria]: 43 43 66412345678

    >>> show ("+43 66412345678", sn_attr, sn_polisher, cc = "43")
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("12345678", sn_attr, sn_polisher)
    sn = 12345678

    >>> show ("0043 664 12345678", sn_attr, sn_polisher)
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("+43 664 12345678", sn_attr, sn_polisher)
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("0043 664 12345678", sn_attr, sn_polisher)
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("664 12345678", sn_attr, sn_polisher)
    sn = 664 12345678

    >>> show ("664 12345678", sn_attr, sn_polisher, cc = "43")
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("664 12345678", sn_attr, sn_polisher, cc = "43", picky = True)
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("664 12345678", sn_attr, sn_polisher, picky = True)
    cc = 66, ndc = 4, sn = 12345678

    >>> show ("0664 12345678", sn_attr, sn_polisher)
    ndc = 664, sn = 12345678

    >>> show ("0 664 12345678", sn_attr, sn_polisher, picky = True)
    ndc = 664, sn = 12345678

    >>> show ("0664 12345678", sn_attr, sn_polisher, picky = True)
    ndc = 664, sn = 12345678

    >>> show ("+43(664)12345678", sn_attr, sn_polisher)
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("+43 (664) 12345678", sn_attr, sn_polisher)
    cc = 43, ndc = 664, sn = 12345678

    >>> show ("0(664)12345678", sn_attr, sn_polisher)
    ndc = 664, sn = 12345678

    >>> show ("0 (664) 12345678", sn_attr, sn_polisher)
    ndc = 664, sn = 12345678

    >>> show ("0(664)12345678", sn_attr, sn_polisher, picky = True)
    ndc = 664, sn = 12345678

    >>> show ("0 (664) 12345678", sn_attr, sn_polisher, picky = True)
    ndc = 664, sn = 12345678

    >>> show ("0 (664) 12345678", sn_attr, sn_polisher, ndc = "699")
    ndc = 664, sn = 12345678

    >>> show ("0664 12345678", sn_attr, sn_polisher, ndc = "699")
    ndc = 664, sn = 12345678

    >>> show ("664 12345678", sn_attr, sn_polisher, ndc = "699")
    ndc = 699, sn = 664 12345678

"""

__test__ = dict \
    ( test_cc   = _test_cc
    , test_ndc  = _test_ndc
    , test_sn   = _test_sn
    )

if __name__ != "__main__" :
    GTW.OMP.PAP.E164._Export_Module ()
### __END__ GTW.OMP.PAP.E164.Polisher
