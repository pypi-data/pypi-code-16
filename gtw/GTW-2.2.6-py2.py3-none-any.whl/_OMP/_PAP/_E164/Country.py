# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.PAP.E164.Country
#
# Purpose
#    Provide phone number mapping for a specific country
#
# Revision Dates
#    23-Jul-2015 (CT) Creation
#    2.-Jul-2015 (CT) Continue creation...
#    31-Jul-2015 (CT) Finish creation
#     3-Aug-2015 (CT) Add `ndc_max_length`, `ndc_min_length`
#     3-Aug-2015 (CT) Make `regexp` argument of `Country_R` optional
#     3-Aug-2015 (CT) Add `formatted_sn`, `formatted_sn_4x2`
#     4-Aug-2015 (CT) Add `M_Country.cc_trie`, `.completions`
#    15-Sep-2015 (CT) Fix guard for `regexp` in `Country_R.__init__`
#    15-Sep-2015 (CT) Change `Country.split` to allow `regexp` without `ndc`
#    15-Sep-2015 (CT) Change `M_Country.__call__` to raise `ValueError`,
#                     not KeyError, for non-existing country codes
#    ««revision-date»»···
#--

from   __future__               import division, print_function
from   __future__               import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

from   _TFL.formatted_repr      import formatted_repr
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.portable_repr       import portable_repr
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import \
    (Regexp, Multi_Regexp, Re_Replacer, Multi_Re_Replacer, re)
from   _TFL.Trie                import Word_Trie as Trie
from   _TFL._Meta.Once_Property import Once_Property

from   _GTW._OMP._PAP._E164     import E164

import _GTW._OMP._PAP._E164.Error

import _TFL._Meta.Object

### Information about national numbering plans can be found at::
###     http://www.itu.int/oth/T0202.aspx?parent=T0202

class M_Country (TFL.Meta.Object.__class__) :
    """Meta class for `Country`."""

    def __call__ (cls, country_code) :
        cc = str (country_code).lstrip ("+")
        try :
            name   = cls.cc_map [cc]
        except KeyError :
            raise ValueError ("Unknown country code %s" % (cc, ))
        try :
            result = cls.Table [cc]
        except KeyError :
            args   = ()
            m_name = "_Country__%s" % cc
            try :
                module = E164._Import_Module (m_name)
                C      = module.Country
            except ImportError :
                try :
                    regexp = cls.ndc_sn_matcher_map [cc]
                    args   = (regexp, )
                    C      = Country_R
                except KeyError :
                    C      = Country_0
            result = cls.Table [cc] = C.__m_super.__call__ (name, cc, * args)
        return result
    # end def __call__

    @Once_Property
    def cc_data (cls) :
        from _GTW._OMP._PAP._E164 import cc_data as result
        return result
    # end def cc_data

    @Once_Property
    def cc_map (cls) :
        "Dictionary mapping country codes to country names."
        return cls.cc_data.cc_map
    # end def cc_map

    @Once_Property
    def cc_matcher_fragment (cls) :
        """Regular expression fragment matching valid country code."""
        sk     = lambda cc : (- len (cc), cc)
        ccs    = sorted (cls.cc_map, key = sk)
        result = "".join (("(?P<cc>", "|".join (ccs), ")"))
        return result
    # end def cc_matcher_fragment

    @Once_Property
    def cc_regexp (cls) :
        return Regexp (r"^ *(?:(?:\+ *|00)?" + cls.cc_matcher_fragment + r")")
    # end def cc_regexp

    @Once_Property
    def cc_regexp_strict (cls) :
        return Regexp (r"^ *(?:(?:\+ *|00)" + cls.cc_matcher_fragment + r")")
    # end def cc_regexp_strict

    @Once_Property
    def cc_trie (cls) :
        """Word trie of country codes."""
        return Trie (cls.cc_map)
    # end def cc_trie

    @Once_Property
    def ndc_data (cls) :
        from _GTW._OMP._PAP._E164 import ndc_data as result
        return result
    # end def ndc_data

    @Once_Property
    def ndc_sn_matcher_map (cls) :
        return cls.ndc_data.ndc_sn_matcher_map
    # end def ndc_sn_matcher_map

    def completions (cls, cc_prefix) :
        """Return all country codes starting with `cc_prefix` and unique
           completion for `cc_prefix`, if any.
        """
        return cls.cc_trie.completions (cc_prefix)
    # end def completions

    def match (cls, phone_number) :
        return cls._match (phone_number, cls.cc_regexp)
    # end def match

    def match_strict (cls, phone_number) :
        return cls._match (phone_number, cls.cc_regexp_strict)
    # end def match_strict

    def _match (cls, phone_number, regexp) :
        match  = regexp.match (phone_number)
        if match :
            return Match (cls (regexp.cc), match, phone_number)
    # end def _match

# end class M_Country

@pyk.adapt__bool__
@pyk.adapt__str__
class Country (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Country)) :
    """Provide phone number mapping for a specific country."""

    Table              = {}

    ###  3-Aug-2015 16:48
    ### https://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers#Denmark
    ### A : ndc digit
    ### B : sn  digit

    format_map = \
        {  "31" : ["AA-BBBBBBB"]                                     # Netherlands
        ,  "32" : ["A BBB BB BB", "AA BB BB BB", "AAA BB BB BB"]     # Belgium
        ,  "33" : ["A BB BB BB BB"]                                  # France
        ,  "34" : ["AAA BBB BBB", "AA B BBB BBB", "A BB BBB BBB"]    # Spain
        , "351" : ["AA BB BB BBB", "AAA BBB BBB"]                    # Portugal
        , "353" : ["AA BBB BBBB"]                                    # Ireland
        , "358" : ["AA BBB BB BB", "A BBB BBB"]                      # Finland
        ,  "36" : ["A BBB BBB", "A BBB BBBB"]                        # Hungary
        ,  "39" : ["AAA BBBBBBB"]                                    # Italy
        ,  "41" : ["AA BBB BB BB"]                                   # Switzerland
        , "420" : ["A BB BBB BBB", "AA B BBB BBB", "AAA BBB BBB"]    # Czech Republic
        ,  "44" : ["AA BBBB BBBB", "AAAA BBB BBBB", "AAAAA BBBBBB"]  # UK
        ,  "45" : ["BB BB BB BB"]                                    # Denmark
        ,  "47" : ["A B BB BB BB", "AA BB BB BB", "AAA BB BBB"]      # Norway
        ,  "48" : ["AA BBB BB BB", "AAA BBB BBB"]                    # Poland
        ,  "49" : ["AAAA BBBBBB"]                                    # Germany
        }
    formatted_sn       = Multi_Re_Replacer \
        ( Re_Replacer (r"^(\d{2,3})(\d{2,3})(\d{2,4})$", r"\1 \2 \3")
        , Re_Replacer (r"^(\d{2})(\d{2,3})$",            r"\1 \2")
        , Re_Replacer (r"^(\d{4})(\d{3,5})(\d{4})$",     r"\1 \2 \3")
        )
    formatted_sn_4x2   = Re_Replacer \
        ( r"^(\d{2})(\d{2})(\d{2})(\d{2})$", r"\1 \2 \3 \4")


    ndc_info_map       = None ### Only available for `Country_M`
    ndc_max_length     = 4
    ndc_min_length     = 1

    ndc_prefix         = "0"

    _number_cleaner    = Re_Replacer (r"[^0-9]", "")

    def __init__ (self, name, code) :
        self.name = name
        self.code = code
    # end def __init__

    @Once_Property
    def ndc_sn_max_length (self) :
        code    = self.code
        default = 15 - len (code)
        return self.__class__.ndc_data.ndc_sn_max_length.get (code, default)
    # end def ndc_sn_max_length

    @Once_Property
    def ndc_sn_min_length (self) :
        code = self.code
        return self.__class__.ndc_data.ndc_sn_min_length.get (code, 5)
    # end def ndc_sn_min_length

    def cleaned_ndc (self, ndc) :
        if ndc :
            return self._number_cleaner (ndc)
    # end def cleaned_ndc

    def cleaned_sn (self, ndc, sn) :
        if sn :
            result = self._number_cleaner (sn)
            l_sn   = len (result)
            max_sn = self.sn_max_length (ndc)
            min_sn = self.sn_min_length (ndc)
            if min_sn > l_sn :
                raise E164.SN_Too_Short \
                    (self, "-".join ((ndc, sn)), l_sn, min_sn)
            elif l_sn > max_sn :
                raise E164.SN_Too_Long \
                    (self, "-".join ((ndc, sn)), l_sn, max_sn)
            else :
                return result
    # end def cleaned_sn

    def ndc_info (self, ndc) :
        pass
    # end def ndc_info

    def sn_max_length (self, ndc) :
        return self.ndc_sn_max_length - len (ndc)
    # end def sn_max_length

    def sn_min_length (self, ndc) :
        return self.ndc_sn_min_length - len (ndc)
    # end def sn_min_length

    def split (self, ndc_sn) :
        regexp  = self.regexp
        match   = regexp.match (ndc_sn)
        if match :
            try :
                r_ndc = regexp.ndc
            except AttributeError :
                ndc = ""
            else :
                ndc = self.cleaned_ndc (r_ndc)
            sn  = self.cleaned_sn  (ndc, regexp.sn)
            return ndc, sn
        raise E164.ValueError (self, ndc_sn, self._split_error_tail (""))
    # end def split

    def _split_error_tail (self, tail) :
        return tail
    # end def _split_error_tail

    def __bool__ (self) :
        return True
    # end def __bool__

    def __repr__ (self) :
        return "%s (%s)" % (_T ("Country"), self.code)
    # end def __repr__

    def __str__ (self) :
        return "%r [%s]" % (self, self.name)
    # end def __str__

# end class Country

@pyk.adapt__bool__
class Country_0 (Country) :
    """Country without further information about ndc and sn."""

    regexp = Multi_Regexp \
        ( Regexp
            ( r" *0? *"
              r"[-/]?"
              r"(?P<ndc>\d{1,4})"
              r"(?:[- /](?P<sn>[- 0-9]+)?)?$"
            )
        , Regexp
            ( r" *0? *"
              r"\("
              r"(?P<ndc>\d{1,4})"
              r"\) *"
              r"(?P<sn>[- 0-9]+)?$"
            )
        )

    def _split_error_tail (self, tail) :
        return \
            ( "".join
                ( ( self.__super._split_error_tail (tail)
                  , "\n    "
                  , _T
                      ( "Network destination code "
                        "and subscriber number need to be separated "
                        "by a space or dash."
                      )
                  )
                )
            )
    # end def _split_error_tail

    def __bool__ (self) :
        return False
    # end def __bool__

# end class Country_0

class Country_M (Country) :
    """Country with a separate module with detailed ndc information"""

    ndc_info_map      = None ### Need to define for country-specific sub-class
    ndc_type_map      = None ### May be defined for country-specific sub-class
    ndc_usage_map     = None ### May be defined for country-specific sub-class
    sn_max_length_map = None ### May be defined for country-specific sub-class
    sn_min_length_map = None ### May be defined for country-specific sub-class

    @Once_Property
    def ndc_matcher_fragment (self) :
        """Regular expression fragment matching national destination code."""
        sk     = lambda ndc : (- len (ndc), ndc)
        ccs    = sorted (self.ndc_info_map, key = sk)
        result = "".join (("(?P<ndc>", "|".join (ccs), ")"))
        return result
    # end def ndc_matcher_fragment

    @Once_Property
    def ndc_prefix_matcher_fragment (self) :
        prefix = self.ndc_prefix
        return r" *(?:%s)? *" % (prefix, ) if prefix else ""
    # end def ndc_prefix_matcher_fragment

    @Once_Property
    def regexp (self) :
        return Multi_Regexp \
            ( Regexp \
                ( self.ndc_prefix_matcher_fragment
                + r"[-/ ]?"
                + self.ndc_matcher_fragment
                + r"[-/ ]?"
                + r"(?P<sn>[- 0-9]+)?$"
                )
            , Regexp \
                ( self.ndc_prefix_matcher_fragment
                + r"\("
                + self.ndc_matcher_fragment
                + r"\) *"
                + r"(?P<sn>[- 0-9]+)?$"
                )
            ,
            )
    # end def regexp

    def ndc_info (self, ndc) :
        try :
            return self.ndc_info_map [ndc]
        except (AttributeError, KeyError) :
            pass
    # end def ndc_info

    def sn_max_length (self, ndc) :
        try :
            result = self.sn_max_length_map [ndc]
        except (AttributeError, LookupError) :
            result = None
        if result is None :
            result = self.__super.sn_max_length (ndc)
        return result
    # end def sn_max_length

    def sn_min_length (self, ndc) :
        try :
            result = self.sn_min_length_map [ndc]
        except (AttributeError, LookupError) :
            result = None
        if result is None :
            result = self.__super.sn_min_length (ndc)
        return result
    # end def sn_min_length

# end class Country_M

class Country_R (Country) :
    """Country with a regexp matching ndc and sn"""

    regexp = None

    def __init__ (self, name, code, regexp = None) :
        self.__super.__init__ (name, code)
        if regexp is not None :
            self.regexp = regexp
    # end def __init__

# end class Country_R

class Match (TFL.Meta.Object) :
    """Match of `Country` for `phone_number`"""

    _ndc         = None
    _sn          = None

    def __init__ (self, country, match, phone_number) :
        self.country      = country
        self.cc           = country.code
        self.match        = match
        self.phone_number = phone_number
    # end def __init__

    @Once_Property
    def attr_dict (self) :
        return dict \
            ( cc  = self.cc
            , ndc = self.ndc
            , sn  = self.sn
            )
    # end def attr_dict

    @property
    def ndc (self) :
        result = self._ndc
        if result is None :
            self._set_ndc_sn ()
            result = self._ndc
        return result
    # end def ndc

    @Once_Property
    def ndc_info (self) :
        return self.country.ndc_info (self.ndc)
    # end def ndc_info

    @Once_Property
    def ndc_sn (self) :
        return self.phone_number [self.match.end ():].strip ()
    # end def ndc_sn

    @property
    def sn (self) :
        result = self._sn
        if result is None :
            self._set_ndc_sn ()
            result = self._sn
        return result
    # end def sn

    def _set_ndc_sn (self) :
        self._ndc, self._sn = self.country.split (self.ndc_sn)
    # end def _set_ndc_sn

    def __repr__ (self) :
        return "Match for %r: %s" % (self.country, self.ndc_sn)
    # end def __repr__

    def __str__ (self) :
        return "Match for %s: %s" % (self.country, self.ndc_sn)
    # end def __str__

# end class Match

_test_country_match = r"""
    >>> AT = Country (43)
    >>> AT
    Country (43)

    >>> m = Country.match ("43 664 123 45 67")
    >>> m.country
    Country (43)

    >>> print (portable_repr (m.ndc_sn))
    '664 123 45 67'

    >>> print (m.ndc_info)
    Mobile (A1)

    >>> m.country is AT
    True

    >>> m.country is Country (43)
    True

    >>> print (Country.match_strict ("43 664 123 45 67"))
    None

    >>> print (Country.match_strict ("+43 664 123 45 67"))
    Match for Country (43) [Austria]: 664 123 45 67

    >>> print (Country.match_strict ("0043 664 123 45 67"))
    Match for Country (43) [Austria]: 664 123 45 67

    >>> print (portable_repr ((m.ndc, m.sn)))
    ('664', '1234567')

    >>> m = Country.match ("436641234567")
    >>> print (portable_repr ((m.ndc, m.sn)))
    ('664', '1234567')

    >>> m = Country.match ("439101234567")
    >>> with expect_except (ValueError) :
    ...     m.country.split (m.ndc_sn)
    ValueError: Not a proper phone number for Country (43) [Austria]: 9101234567

    >>> m = Country.match ("+41 43 123 45 67")
    >>> print (m.country)
    Country (41) [Switzerland (Confederation of)]

    >>> print (m.ndc_info)
    Zurich

    >>> print (portable_repr ((m.ndc, m.sn)))
    ('43', '1234567')

    >>> m = Country.match ("3861 123 45 67")
    >>> print (m.country)
    Country (386) [Slovenia (Republic of)]

    >>> print (m.ndc_info)
    Ljubljana

    >>> print (portable_repr ((m.ndc, m.sn)))
    ('1', '1234567')

    >>> m = Country.match ("38651 123 456")
    >>> print (portable_repr ((m.ndc, m.sn)))
    ('51', '123456')

    >>> print (m.ndc_info)
    Telekom Slovenije

    >>> m = Country.match ("38671 123 45 67")
    >>> with expect_except (ValueError) :
    ...     m.ndc
    SN_Too_Long: Not a proper phone number for Country (386) [Slovenia (Republic of)]: 71-123 45 67; subscriber number must have at most 6 digits; got 7 digits instead

    >>> m = Country.match ("+49 89 123 45 67")
    >>> print (m.country)
    Country (49) [Germany (Federal Republic of)]

    >>> print (m.ndc_info)
    None

    >>> print (portable_repr ((m.ndc, m.sn)))
    ('89', '1234567')

    >>> m = Country.match ("+49891234567")
    >>> print (m.country)
    Country (49) [Germany (Federal Republic of)]

    >>> with expect_except (ValueError) :
    ...     print (portable_repr ((m.ndc, m.sn)))
    ValueError: Not a proper phone number for Country (49) [Germany (Federal Republic of)]: 891234567
        Network destination code and subscriber number need to be separated by a space or dash.

    >>> m = Country.match ("+39 045 1234567")
    >>> print (m.ndc_info)
    Province of Verona
    >>> print (portable_repr ((m.ndc, m.sn)))
    ('045', '1234567')

    >>> m = Country.match ("+39 045 123456789")
    >>> with expect_except (ValueError) :
    ...     print (portable_repr ((m.ndc, m.sn)))
    SN_Too_Long: Not a proper phone number for Country (39) [Italy, Vatican]: 045-123456789; subscriber number must have at most 8 digits; got 9 digits instead

    >>> m = Country.match ("+39 045 12345")
    >>> with expect_except (ValueError) :
    ...     print (portable_repr ((m.ndc, m.sn)))
    SN_Too_Short: Not a proper phone number for Country (39) [Italy, Vatican]: 045-12345; subscriber number must have at least 6 digits; got 5 digits instead

"""

__test__ = dict \
    ( test_country_match = _test_country_match
    )

if __name__ != "__main__" :
    GTW.OMP.PAP.E164._Export ("*")
### __END__ GTW.OMP.PAP.E164.Country
