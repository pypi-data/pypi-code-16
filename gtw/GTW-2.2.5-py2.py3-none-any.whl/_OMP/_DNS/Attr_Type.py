# -*- coding: utf-8 -*-
# Copyright (C) 2012 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A-3411 Weidling, Austria. rsc@runtux.com
# #*** <License> ************************************************************#
# This module is part of the package FFM.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    FFM.Attr_Type
#
# Purpose
#    Define attribute types for package FFM
#
# Revision Dates
#    27-Aug-2012 (RS) Creation
#    22-Sep-2012 (RS) Factor `A_DNS_Label` and correct syntax
#    11-Oct-2012 (RS) RFC 1123 section 2.1 permits DNS label
#                     to start with a digit, change `A_DNS_Label` syntax
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *
from   _MOM.import_MOM          import _A_Composite_, _A_Named_Value_
from   _MOM.import_MOM          import _A_Unit_, _A_Int_
from   _GTW._OMP._DNS           import DNS
from   _TFL.I18N                import _
from   _TFL.Regexp              import Regexp

class A_DNS_Time (_A_Unit_, _A_Int_) :
    """ Allow specification of DNS times in other units than seconds """

    typ             = _ ("DNS Time")
    needs_raw_value = True
    min_value       = 0
    max_value       = 2147483647
    _unit_dict      = dict \
        ( seconds   = 1
        , minutes   = 60
        , hours     = 60 * 60
        , days      = 60 * 60 * 24
        , weeks     = 60 * 60 * 24 * 7
        )

# end class A_DNS_Time

class A_DNS_Label (Syntax_Re_Mixin, A_String) :
    """ A single DNS label (without dots)
        See rfc1034 *and* rfc1123 section 2.1 for details.
    """

    max_length      = 63
    ignore_case     = True
    syntax          = _ \
        ( u"A label starts"
           " with a letter or digit and is optionally followed by letters,"
           " digits or dashes and ends with a letter or digit. "
           "A label may be up to 63 characters long."
        )
    _label          = r"[a-zA-Z0-9](?:[-a-zA-Z0-9]{0,61}[a-zA-Z0-9])?"
    _syntax_re      = Regexp (_label)

# end class A_DNS_Label

class A_DNS_Name (Syntax_Re_Mixin, A_String) :
    """ DNS name consisting of labels separated by '.'
        See rfc1034 for details.
    """

    max_length      = 253
    ignore_case     = True
    syntax          = _ \
        ( u"DNS name must consist of up to 127 labels. ") + A_DNS_Label.syntax
    _syntax_re      = Regexp \
        (r"%s([.]%s){0,126}" % (A_DNS_Label._label, A_DNS_Label._label))

# end class A_DNS_Name

if __name__ != "__main__" :
    GTW.OMP.DNS._Export ("*")
### __END__ GTW.OMP.DNS.Attr_Type
