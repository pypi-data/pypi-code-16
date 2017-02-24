# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.Auth.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.Auth.Certificate
#
# Purpose
#    Certificate that can be used to authenticate an account
#
# Revision Dates
#    11-Jan-2013 (CT) Creation
#    14-Jan-2013 (CT) Add `pem` to `alive.query_fct`
#    16-Jan-2013 (CT) Replace `is_revoked` by `revocation_date`
#    25-Feb-2013 (CT) Replace `alive.auto_up_depends` by `.query_preconditions`
#    25-Feb-2013 (CT) Simplify `alive.query_fct` by relying on
#                     `.query_preconditions`
#    26-Apr-2013 (CT) Remove `cert_id`, make `email`, `validity`, `desc` primary
#     5-Jun-2013 (CT) Add `cert_id` again, now as `A_Surrogate`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM               import *
from   _GTW                          import GTW

from   _GTW._OMP._Auth               import Auth
import _GTW._OMP._Auth.Entity

from   _MOM._Attr.Date_Time_Interval import *

from   _TFL.I18N                     import _, _T, _Tn

_Ancestor_Essence = Auth.Object

class Certificate (_Ancestor_Essence) :
    """Certificate that can be used to authenticate an account."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class email (A_Email) :
            """Email of account"""

            kind               = Attr.Primary

        # end class email

        class validity (A_Date_Time_Interval) :
            """Validity date interval"""

            kind               = Attr.Primary

        # end class validity

        class desc (A_String) :
            """Short description of the certificate"""

            kind               = Attr.Primary_Optional
            max_length         = 40
            ui_name            = _("Description")

        # end class desc

        ### Non-primary attributes

        class cert_id (A_Surrogate) :
            """Id of certificate"""

        # end class cert_id

        class revocation_date (A_Date_Time) :
            """Date and time when the certificate was revoked"""

            kind               = Attr.Optional

        # end class revocation_date

        class pem (Attr._A_Binary_String_) :
            """Signed certificate"""

            kind               = Attr.Internal

        # end class pem

        class alive (A_Boolean) :
            """Specifies whether the certificate is currently alive, i.e.,
               it isn't revoked and the current date lies between
               `validity.start` and `validity.finish`.
            """

            kind                   = Attr.Query
            ### need to recompute each time `alive` is accessed
            Kind_Mixins            = (Attr.Computed, )
            query_preconditions    = (Q.validity.start, )

            def query_fct (self) :
                now = A_Date_Time.now ()
                return \
                    ( ((Q.validity.finish == None) | (now <= Q.validity.finish))
                    & ( Q.validity.start  <= now)
                    & ( Q.revocation_date == None)
                    & ( Q.pem             != None)
                    )
            # end def query_fct

        # end class alive

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        _Ancestor = _Ancestor_Essence._Predicates

        class valid_revocation_date (Pred.Condition) :
            """The revocation date cannot be in the future."""

            kind               = Pred.Object
            assertion          = "revocation_date <= today"
            attributes         = ("revocation_date",)
            bindings           = dict (today = "this.today")

        # end class valid_revocation_date

    # end class _Predicates

    @property
    def today (self) :
        return A_Date_Time.now ().replace \
            (hour = 0, minute = 0, second = 0, microsecond = 0)
    # end def today

# end class Certificate

if __name__ != "__main__" :
    GTW.OMP.Auth._Export ("*")
### __END__ GTW.OMP.Auth.Certificate
