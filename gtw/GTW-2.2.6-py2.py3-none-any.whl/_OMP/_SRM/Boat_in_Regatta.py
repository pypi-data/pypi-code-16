# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SRM.Boat_in_Regatta
#
# Purpose
#    Boat racing in a regatta
#
# Revision Dates
#    19-Apr-2010 (CT) Creation
#    10-May-2010 (CT) `place` added
#     6-Sep-2010 (CT) `race_results` removed (now implemented as `Link1`)
#    20-Sep-2010 (CT) `rank` added
#    14-Oct-2010 (CT) `Init_Only_Mixin` added to `registration_date`
#     1-Dec-2010 (CT) `crew` added
#    22-Sep-2011 (CT) s/A_Entity/A_Id_Entity/
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    26-Jan-2012 (CT) Set `Boat_in_Regatta.left.ui_allow_new`
#    27-Apr-2012 (CT) Add predicate `skipper_not_multiplexed`
#     7-May-2012 (CT) Add predicate `crew_number_valid`, change
#                     `crew` from `Cached, Computed_Set_Mixin` to `Computed`
#    23-Jul-2012 (CT) Use `Link_Cacher` for auto-cached `boats`
#     7-Aug-2012 (CT) Add `example`
#    30-Jan-2013 (CT) Replace `skipper_not_multiplexed` by
#                     `unique_regatta_skipper`
#    12-May-2013 (CT) Repace `auto_cache` by `link_ref_attr_name`
#    13-May-2013 (CT) Use `query`, not `r_query`
#    30-Jan-2014 (CT) Add attribute `ranking_list_points_lp`
#    17-Aug-2014 (CT) Remove attribute `ranking_list_points_lp`
#    28-Apr-2015 (CT) Add `_A_Id_Entity_List_` to bases of `crew`
#    29-Apr-2015 (CT) Change `crew_number_valid` to use `_crew`, not `crew`
#    25-Oct-2015 (CT) Add optional attribute `yardstick`
#    ««revision-date»»···
#--

from   __future__               import unicode_literals, division

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._SRM.Boat
import _GTW._OMP._SRM.Entity
import _GTW._OMP._SRM.Regatta
import _GTW._OMP._SRM.Sailor

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SRM.Link2

class Boat_in_Regatta (_Ancestor_Essence) :
    """Boat racing in a regatta."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Boat racing in a regatta."""

            role_type          = GTW.OMP.SRM.Boat
            ui_allow_new       = True

        # end class left

        class right (_Ancestor.right) :
            """Regatta a boat races in."""

            role_type          = GTW.OMP.SRM.Regatta
            link_ref_attr_name = "boats"
            link_ref_suffix    = None

        # end class right

        ### Non-primary attributes

        class crew (MOM.Attr._A_Id_Entity_List_, A_Blob) :

            kind               = Attr.Computed
            P_Type             = GTW.OMP.SRM.Sailor

            def computed (self, obj) :
                scope = obj.home_scope
                return \
                    [ cm.sailor for cm in scope.SRM.Crew_Member.query
                        ( left = obj
                        , sort_key = TFL.Sorted_By ("key", "pid")
                        )
                    ]
            # end def computed

        # end class crew

        class place (A_Int) :
            """Place of boat in this regatta."""

            kind               = Attr.Optional
            example            = 2
            min_value          = 1

        # end class place

        class points (A_Int) :
            """Total points of boat in this regatta."""

            kind               = Attr.Optional
            example            = 25
            min_value          = 1

        # end class points

        class rank (A_Int) :
            """Rank of registration of boat in regatta."""

            kind               = Attr.Internal
            default            = 0
            example            = 13

        # end class rank

        class registration_date (A_Date) :
            """Date of registration."""

            kind               = Attr.Internal
            Kind_Mixins        = (Attr.Init_Only_Mixin, )
            computed_default   = A_Date.now

        # end class registration_date

        class skipper (A_Id_Entity) :
            """Skipper of boat."""

            P_Type             = GTW.OMP.SRM.Sailor
            kind               = Attr.Required

        # end class skipper

        class yardstick (A_Int) :
            """Yardstick number of boat."""

            kind               = Attr.Optional
            default            = 100
            example            = 107
            min_value          = 50

        # end class yardstick

        class other_boots_skippered (A_Blob) :
            """Other links of this `skipper` to a boat in this `regatta.event`.
            """

            kind               = Attr.Computed

            def computed (self, obj) :
                if obj is not None :
                    ETM = obj.home_scope [obj.type_name]
                    return ETM.query_s \
                        ( Q.pid           != obj.pid
                        , Q.regatta.event == obj.regatta.event
                        , Q.skipper       == obj.skipper
                        )
            # end def computed

        # end class other_boots_skippered

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        _Ancestor = _Ancestor_Essence._Predicates

        class crew_number_valid (Pred.Condition) :
            """The number of crew members must be less than
               `boat.b_class.max_crew`.
            """

            kind                 = Pred.Region
            assertion            = "number_of_crew < boat.b_class.max_crew"
            attributes           = ("boat.b_class.max_crew", "_crew")
            bindings             = dict \
                ( number_of_crew = "len (_crew)"
                )

        # end class crew_number_valid

        unique_regatta_skipper = Pred.Unique.New_Pred \
            ( "regatta", "skipper"
            , name    = "unique_regatta_skipper"
            , __doc__ =
                """A sailor can't be skipper of more than one boat in a single
                   regatta event.
                """
            )

    # end class _Predicates

# end class Boat_in_Regatta

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Boat_in_Regatta
