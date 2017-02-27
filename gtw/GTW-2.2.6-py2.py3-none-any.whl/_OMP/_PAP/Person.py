# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.PAP.Person
#
# Purpose
#    Model a Person
#
# Revision Dates
#    30-Dec-2009 (CT) Creation
#    14-Jan-2010 (CT) `ui_name` added to some attributes
#    29-Jan-2010 (CT) `middle_name` added
#    10-Feb-2010 (CT) `birth_date (A_Date)` replaced by `date (A_Lifetime)`
#    22-Feb-2010 (CT) `ignore_case` set for primary attributes
#    24-Feb-2010 (CT) s/Lifetime/Date_Interval/
#    10-May-2010 (CT) `ui_display_format` redefined
#     4-Jun-2010 (CT) `sex` added
#    13-Oct-2010 (CT) `example` added
#     8-Jun-2011 (MG) `_AC_Query_LN_` and `last_name.ac_query` added
#     9-Jun-2011 (MG) `_AC_Query_LN_` enhanced
#     6-Jul-2011 (CT) s/_AC_Query_LN_/_AC_Query_FL_/, added to `first_name`, too
#     6-Jul-2011 (CT) `e_completer` added to primary attributes
#     6-Jul-2011 (CT) `f_completer` added to primary attributes and `salutation`
#    16-Jul-2011 (CT) `_AC_Query_FL_` derived from (newly factored) `_AC_Query_S_`
#    17-Jul-2011 (CT) s/f_completer/completer/, removed `e_completer`
#    12-Sep-2011 (CT) `prefix` added to `_AC_Query_FL_.query`
#    25-Oct-2011 (CT) `ui_display_format` format changed (put `last_name` first)
#    11-Nov-2011 (CT) Adapt to change of `MOM.Attr.Filter`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     4-Dec-2011 (CT) Adapt to factoring of `MOM.Attr.Querier` from
#                     `MOM.Attr.Filter`
#     6-Mar-2012 (CT) Factor `Subject`
#    22-Mar-2013 (CT) Set `Subject.default_child` to `Person`
#     9-Jan-2014 (CT) Remove attribute `salutation`
#    16-Apr-2014 (CT) Add query attribute `my_person`
#    12-Sep-2014 (CT) Remove `my_person`
#                     [use type restriction in queries, instead]
#    24-Sep-2014 (CT) Add `polisher` to `last_name`, `first_name`, `middle_name`
#    26-Sep-2014 (CT) Use `Polisher.capitalize_if_not_mixed_case`,
#                     not `.capitalize`
#    26-Sep-2014 (CT) Add `polisher = capitalize_if_lower_case` to `title`
#    23-Jan-2015 (CT) Add `title.ui_name_short`
#    14-Apr-2015 (CT) Lower completer tresholds
#     3-Aug-2015 (CT) Set `_init_raw_default` to `True`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM             import *
from   _MOM._Attr.Date_Interval    import *

from   _GTW._OMP._PAP.Attr_Type    import *

from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP
from   _TFL.I18N                   import _
import _TFL.Decorator

import _GTW._OMP._PAP.Subject

class Auto_Complete_PN (MOM.Attr.Filter.Auto_Complete_S) :
    """Special auto-complete query filter for the `first_name` and
       `last_name` of a person (to better handling of double names like
       Franz-Ferdinand).
    """

    def query (self, value) :
        aq = self.a_query
        if value == "" :
            return aq.__eq__ (value)
        elif "-" in value :
            return aq.STARTSWITH (value)
        else :
            pvalue = "-%s" % (value, )
            return aq.STARTSWITH (value) | aq.CONTAINS (pvalue)
    # end def query

# end class Auto_Complete_PN

class Filter_String_FL (MOM.Attr.Querier.String) :

    _real_name = "String_FL"
    _Table     = dict (AC = Auto_Complete_PN)

# end class Filter_String_FL

_Ancestor_Essence = PAP.Subject

@TFL.Add_To_Class ("default_child", _Ancestor_Essence)
class _PAP_Person_ (_Ancestor_Essence) :
    """Model a person."""

    _real_name             = "Person"

    _init_raw_default      = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class _personal_name_ (A_String) :

            kind           = Attr.Primary
            ignore_case    = True
            Q_Ckd_Type     = Filter_String_FL

        # end class _personal_name_

        class last_name (_personal_name_) :
            """Last name of person"""

            example        = u"Doe"
            max_length     = 48
            rank           = 1

            completer      = Attr.Completer_Spec  (1, Attr.Selector.primary)
            polisher       = Attr.Polisher.capitalize_last_word_compress_spaces

        # end class last_name

        class first_name (_personal_name_) :
            """First name of person"""

            example        = u"John"
            max_length     = 32
            rank           = 2

            completer      = Attr.Completer_Spec  (1, Attr.Selector.primary)
            polisher       = \
                Attr.Polisher.capitalize_if_not_mixed_case_compress_spaces

        # end class first_name

        class middle_name (A_String) :
            """Middle name of person"""

            kind           = Attr.Primary_Optional
            ignore_case    = True
            example        = "F."
            max_length     = 32
            rank           = 1

            completer      = Attr.Completer_Spec  (1, Attr.Selector.primary)
            polisher       = \
                Attr.Polisher.capitalize_if_not_mixed_case_compress_spaces

        # end class middle_name

        class title (A_String) :
            """Academic title"""

            kind           = Attr.Primary_Optional
            ignore_case    = True
            example        = "Dr."
            max_length     = 20
            rank           = 2
            ui_name        = _("Academic title")
            ui_name_short  = _("Title")

            completer      = Attr.Completer_Spec  (0)
            polisher       = \
                Attr.Polisher.capitalize_if_lower_case_compress_spaces

        # end class title

        ### Non-primary attributes

        class sex (A_Sex) :

            kind           = Attr.Necessary

        # end class sex

    # end class _Attributes

    @property
    def ui_display_format (self) :
        result = ["%(last_name)s %(first_name)s"]
        if self.middle_name :
            result.append (" %(middle_name)s")
        if self.title :
            result.append (", %(title)s")
        return "".join (result)
    # end def ui_display_format

Person = _PAP_Person_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Person
