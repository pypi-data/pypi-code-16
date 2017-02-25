# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.VAT_IDN
#
# Purpose
#    Encapsulate VAT identification number
#
# Revision Dates
#     8-Feb-2016 (CT) Creation
#    24-Feb-2016 (CT) Change `VAT_IDN.__init__` to accept `VAT_IDN` instances
#    25-Feb-2016 (CT) Add `__eq__`, `__hash__`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._PAP

from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import Regexp, Re_Replacer, re

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL._Meta.Property

### https://en.wikipedia.org/wiki/VAT_identification_number

class _Country_Rule_ (TFL.Meta.Object) :
    """Rule for VAT id-numbers of a specific country.

       >>> VAT_IDN ("ATU99999999")
       ATU99999999
       >>> VAT_IDN ("ATU999999990")
       Traceback (most recent call last):
         ...
       ValueError: Invalid VAT identification number ATU999999990

       >>> VAT_IDN ("BE0999999999")
       BE0999999999

       >>> VAT_IDN ("BG99999999")
       Traceback (most recent call last):
         ...
       ValueError: Invalid VAT identification number BG99999999

       >>> VAT_IDN ("HR12345678901")
       HR12345678901
       >>> VAT_IDN ("HR12345678903")
       Traceback (most recent call last):
         ...
       ValueError: Invalid VAT identification number HR12345678903

       >>> VAT_IDN ("CZ12345678")
       CZ12345678
       >>> VAT_IDN ("CZ123456789")
       CZ123456789
       >>> VAT_IDN ("CZ1234567890")
       CZ1234567890

       >>> VAT_IDN ("DK99999999")
       DK99999999

       >>> VAT_IDN ("EE123456789")
       EE123456789

       >>> VAT_IDN ("FR83,404,833,048")
       FR83404833048

       >>> VAT_IDN ("NL999999999B99")
       NL999999999B99

       >>> VAT_IDN ("ESX9999999X")
       ESX9999999X

       >>> VAT_IDN ("GB999 9999 73")
       GB999999973

       >>> VAT_IDN ("CHE-123.456.788")
       CHE123456788
       >>> VAT_IDN ("CHE109322551")
       CHE109322551

    """

    checker       = None
    Table         = {}

    def __new__ (cls, cc, country, pat, ** kw) :
        cc    = cc.upper ()
        pat   = Regexp   ("^" + pat + "$")
        Table = cls.Table
        if cc in Table :
            ex = Table [cc]
            raise ValueError \
                ( "Rule for %s is already defined as %s; got %s"
                % (cc, ex.pat._pattern.pattern, pat._pattern.pattern)
                )
        result = Table [cc] = cls.__c_super.__new__ \
            (cls, cc, country, pat, ** kw)
        result._init_ (cc, country, pat, ** kw)
        return result
    # end def __new__

    def _init_ (self, cc, country, pat, ** kw) :
        self.cc      = cc
        self.country = country
        self.pat     = pat
        self.__dict__.update (kw)
    # end def _init_

    def __call__ (self, vin) :
        """Check `vin` for syntactic validity."""
        checker = self.checker
        result  = bool (self.pat.match (vin))
        if result and checker is not None :
            result = checker (vin)
        return result
    # end def __call__

    @classmethod
    def ch_checker (cls, vin) :
        key      = int (vin [-1])
        digits   = list (int (i) for i in vin [1:-1])
        weights  = (5, 4, 3, 2, 7, 6, 5, 4)
        w_sum    = sum (a * b for a, b in zip (digits, weights))
        checksum = 11 - (w_sum % 11)
        return key == checksum
    # end def ch_checker

    @classmethod
    def fr_checker (cls, vin) :
        key   = int (vin [:2])
        siren = int (vin [2:])
        return key == ((12 + 3 * (siren % 97)) % 97)
    # end def fr_checker

    @classmethod
    def iso_7064_mod11_10 (cls, vin) :
        result = 0
        for i in vin :
            result = (((result or 10) * 2) % 11 + int (i)) % 10
        return result == 1
    # end def iso_7064_mod11_10

    @classmethod
    def mod11 (cls, vin) :
        return not (vin % 11)
    # end def mod11

# end class _Country_Rule_

### EU
_Country_Rule_ ( "AT", _ ("Austria"),         r"U\d{8}")
_Country_Rule_ ( "BE", _ ("Belgium"),         r"[01]\d{9}")
_Country_Rule_ ( "BG", _ ("Bulgaria"),        r"\d{9,10}")
_Country_Rule_ ( "CZ", _ ("Czech Republic "), r"\d{8,10}")
_Country_Rule_ ( "DE", _ ("Germany"),         r"\d{9}")
_Country_Rule_ ( "DK", _ ("Denmark"),         r"\d{8}")
_Country_Rule_ ( "EE", _ ("Estland"),         r"\d{9}")
_Country_Rule_ ( "EL", _ ("Greece"),          r"\d{9}")
_Country_Rule_ ( "ES", _ ("Spain"),           r"[A-Z0-9]\d{7}[A-Z0-9]")
_Country_Rule_ ( "FI", _ ("Finland"),         r"\d{8}")
_Country_Rule_ ( "FR", _ ("France"),          r"\d{2}\d{9}"
               , checker = _Country_Rule_.fr_checker
               )
_Country_Rule_ ( "GB", _ ("United Kingdom"),  r"\d{9}(?:\d{3})?")
_Country_Rule_ ( "HR", _ ("Croatia"),         r"\d{11}"
               , checker = _Country_Rule_.iso_7064_mod11_10
               )
_Country_Rule_ ( "HU", _ ("Hungary"),         r"\d{8}")
_Country_Rule_ ( "IE", _ ("Ireland"),         r"\d{7}[A-Z]{1,2}")
_Country_Rule_ ( "IT", _ ("Italy"),           r"\d{11}")
_Country_Rule_ ( "LT", _ ("Lithuania"),       r"\d{9}(?:\d{3})?")
_Country_Rule_ ( "LU", _ ("Luxembourg"),      r"\d{8}")
_Country_Rule_ ( "LV", _ ("Latvia"),          r"\d{11}")
_Country_Rule_ ( "MT", _ ("Malta"),           r"\d{8}")
_Country_Rule_ ( "NL", _ ("Netherlands"),     r"\d{9}B\d{2}")
_Country_Rule_ ( "PL", _ ("Poland"),          r"\d{10}")
_Country_Rule_ ( "PT", _ ("Portugal"),        r"\d{9}")
_Country_Rule_ ( "RO", _ ("Romania"),         r"\d{2,10}")
_Country_Rule_ ( "SE", _ ("Sweden"),          r"\d{12}")
_Country_Rule_ ( "SI", _ ("Slovenia"),        r"\d{8}")
_Country_Rule_ ( "SK", _ ("Slovakia"),        r"\d{10}"
               , checker = _Country_Rule_.mod11
               )

### Switzerland
_Country_Rule_ ( "CH", _ ("Switzerland"),     r"E\d{9}"
               , checker = _Country_Rule_.ch_checker
               )

@pyk.adapt__str__
class VAT_IDN (TFL.Meta.Object) :
    """Value added tax identification number"""

    Countries     = _Country_Rule_.Table
    _cleaned      = Re_Replacer ("[- .,]", "")
    _value        = None

    def __init__ (self, vin) :
        value       = vin.value \
            if isinstance (vin, VAT_IDN) else self._cleaned (vin.upper ())
        self.cc     = value [:2]
        self.idn    = value [2:]
        self._value = value
        rule        = self.rule
        if rule is not None and not rule (self.idn) :
            raise ValueError (_T ("Invalid VAT identification number %s" % vin))
    # end def __init__

    @TFL.Meta.Once_Property
    def rule (self) :
        try :
            return self.Countries [self.cc]
        except KeyError :
            pass
    # end def rule

    @property
    def value (self) :
        return self._value
    # end def value

    def __eq__ (self, rhs) :
        r = rhs.value if isinstance (rhs, VAT_IDN) else rhs
        return self.value == r
    # end def __eq__

    def __hash__ (self) :
        return hash (self.value)
    # end def __hash__

    def __repr__ (self) :
        return pyk.reprify (self.value)
    # end def __repr__

    def __str__ (self) :
        return "%s" % (self.value, )
    # end def __str__

# end class VAT_IDN

class A_VAT_IDN (A_Attr_Type) :
    """VAT identification number"""

    typ               = "VAT-IDN"
    max_length        = 14      ### two-letter country code + 2–12 characters
    max_ui_length     = 20      ### allow spaces, dashes, periods as separators
    P_Type            = VAT_IDN
    Pickler           = Pickler_As_String

# end class A_VAT_IDN

__attr_types = Attr.attr_types_of_module ()
__all__      = __attr_types + ("VAT_IDN", )

if __name__ != "__main__" :
    GTW.OMP.PAP._Export (* __all__)
### __END__ GTW.OMP.PAP.VAT_IDN
