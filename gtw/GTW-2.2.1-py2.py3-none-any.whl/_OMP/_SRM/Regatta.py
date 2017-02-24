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
#    GTW.OMP.SRM.Regatta
#
# Purpose
#    Model a sailing regatta for one class or handicap
#
# Revision Dates
#    15-Apr-2010 (CT) Creation
#     5-May-2010 (CT) Cached attributes added
#     5-May-2010 (CT) `perma_name` defined as `Attr.Internal` to allow queries
#     7-May-2010 (CT) `year` added
#    10-May-2010 (CT) `discards` and `races` added
#    11-May-2010 (CT) `result` added
#    31-Aug-2010 (CT) `is_team_race` added to `Regatta_C`
#     6-Sep-2010 (MG) `Regatta.is_relevant` added
#    21-Sep-2010 (CT) `Regatta_H.is_team_race` added
#    23-Nov-2010 (CT) `kind` added
#    14-Dec-2010 (CT) `year` changed from `Query` to `Cached`
#    22-Sep-2011 (CT) s/A_Entity/A_Id_Entity/
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     2-Feb-2012 (CT) Don't apply `sanitized_filename` to `name`
#     9-Mar-2012 (CT) Change `Regatta_C.name.computed` to use `.ui_display`
#    19-Mar-2012 (CT) Factor `boat_class` to `Regatta`, reify `SRM.Handicap`
#    20-Apr-2012 (CT) Add `Regatta_H.handicap` to fix jinja template that
#                     depends on it
#    30-May-2012 (CT) Add attribute `is_cancelled`
#     7-Aug-2012 (CT) Define `Regatta.default_child`
#    21-Mar-2013 (CT) Set `Regatta.boat_class.P_Type_S` to avoid
#                     `polymorphic_epk`
#    17-Apr-2013 (CT) Use `Computed_Set_Mixin`, not `Computed_Mixin`
#    10-May-2013 (CT) Replace `auto_cache` by `link_ref_attr_name`
#    25-Jun-2013 (CT) Add `max_value`, `example`, to integer attributes
#    17-Jan-2014 (CT) Change attributes `year`, `handicap` to `Attr.Query`
#    17-Jan-2014 (CT) Add query attribute `races_counted`
#    30-Jan-2014 (CT) Add attributes `ranking_list_factor`, `starters`
#    17-Aug-2014 (CT) Remove attribute `ranking_list_factor`
#     3-Feb-2015 (CT) Add `max_crew`
#    25-Oct-2015 (CT) Add `compute_yardstick_results`, `yardstick_time`
#    ««revision-date»»···
#--

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

from   _GTW._OMP._SRM.Attr_Type import A_Regatta_Result

import _GTW._OMP._SRM.Boat_Class
import _GTW._OMP._SRM.Regatta_Event

from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import dusplit
from   _TFL.pyk                 import pyk

import _TFL.Decorator

_Ancestor_Essence = GTW.OMP.SRM.Link1

class Regatta (_Ancestor_Essence) :
    """Sailing regatta for one class or handicap."""

    is_partial  = True
    is_relevant = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Regatta event to which this regatta belongs."""

            role_type          = GTW.OMP.SRM.Regatta_Event
            role_name          = "event"
            link_ref_attr_name = "regatta"
            ui_allow_new       = True

        # end class left

        class boat_class (A_Id_Entity) :
            """Class of boats sailing in this regatta."""

            kind               = Attr.Primary
            P_Type = P_Type_S  = GTW.OMP.SRM._Boat_Class_

        # end class boat_class

        ### Non-primary attributes

        class discards (A_Int) :
            """Number of discardable races in regatta"""

            kind               = Attr.Optional
            default            = 0
            example            = "1"
            max_value          = 32
            min_value          = 0

        # end class discards

        class is_cancelled (A_Boolean) :
            """Indicates that the regatta is cancelled"""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )

            def computed (self, obj) :
                return obj.event.is_cancelled
            # end def computed

        # end class is_cancelled

        class kind (A_String) :
            """Kind of regatta."""

            kind               = Attr.Optional
            example            = "One race, one beer"
            max_length         = 32
            completer          = Attr.Completer_Spec  (1)

        # end class kind

        class name (A_String) :

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("boat_class", )

            def computed (self, obj) :
                return obj.boat_class.ui_display
            # end def computed

        # end class name

        class perma_name (A_String) :

            kind               = Attr.Internal
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("name", )

            def computed (self, obj) :
                return pyk.decoded \
                    (TFL.Ascii.sanitized_filename (obj.name).lower ())
            # end def computed

        # end class perma_name

        class races (A_Int) :
            """Number of races sailed in regatta"""

            kind               = Attr.Optional
            default            = 0
            example            = "7"
            max_value          = 32
            min_value          = 0

        # end class races

        class races_counted (A_Int) :
            """Number of races counted for result of regatta."""

            kind               = Attr.Query
            query              = Q.races - Q.discards

        # end class races_counted

        class result (A_Regatta_Result) :
            """Information about result."""

            kind               = Attr.Optional

        # end class result

        class short_title (A_String) :

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("name", )

            def computed (self, obj) :
                return TFL.Ascii.sanitized_filename (obj.name)
            # end def computed

        # end class short_title

        class starters_rl (A_Int) :
            """Number of boats participating in the regatta as relevant for
               for low-point based formula for ranking list points.
            """

            kind               = Attr.Optional
            explanation        = """
                This is the number of boats that actually participated in the
                `regatta`. If the regatta field was split into groups, it is
                the maximum number of starters of any group.
            """

        # end class starters_rl

        class title (A_String) :

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            max_length         = 128
            auto_up_depends    = ("left", "name")

            def computed (self, obj) :
                return ", ".join ((obj.left.title, obj.name))
            # end def computed

        # end class title

        class year (A_Int) :

            kind               = Attr.Query
            query              = Q.left.year

        # end class year

    # end class _Attributes

# end class Regatta

_Ancestor_Essence = Regatta

@TFL.Add_To_Class ("default_child", Regatta)
class Regatta_C (_Ancestor_Essence) :
    """Regatta for a single class of sail boats."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class boat_class (_Ancestor.boat_class) :

            P_Type             = GTW.OMP.SRM.Boat_Class

        # end class boat_class

        class is_team_race (A_Boolean) :

            kind               = Attr.Optional
            default            = False

        # end class is_team_race

        class max_crew (A_Int) :

            kind               = Attr.Query
            query              = Q.boat_class.max_crew

        # end class max_crew

    # end class _Attributes

# end class Regatta_C

_Ancestor_Essence = Regatta

class Regatta_H (_Ancestor_Essence) :
    """Regatta for boats in a handicap system."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class boat_class (_Ancestor.boat_class) :
            """Name of handicap system used for this regatta."""

            P_Type             = GTW.OMP.SRM.Handicap
            ui_name            = "Handicap"

        # end class boat_class

        class is_team_race (A_Boolean) :

            kind               = Attr.Const
            default            = False

        # end class is_team_race

        class handicap (A_Blob) :

            kind               = Attr.Query
            query              = Q.boat_class

        # end class handicap

        class max_crew (A_Int) :

            kind               = Attr.Const
            default            = 0

        # end class max_crew

    # end class _Attributes

    def compute_yardstick_results (self) :
        sort_key = TFL.Sorted_By (Q.time_corrected, Q.left.yardstick)
        SRM      = self.home_scope.SRM
        ys_time  = self.yardstick_time
        for race_times in dusplit \
                (SRM.Race_Time.query (Q.left.right == self).all (), Q.race) :
            for rt in race_times :
                rt.time_corrected = ys_time (rt.left.yardstick, rt.time)
            for i, rt in enumerate (sorted (race_times, key = sort_key)) :
                SRM.Race_Result.instance (rt.left, rt.race, points = i)
    # end def compute_yardstick_results

    def yardstick_time (self, ys_factor, seconds) :
        """Return corrected time for elapsed time `seconds` and yardstick
           factor `ys_factor`.
        """
        return (seconds * 100.0) / ys_factor
    # end def yardstick_time

# end class Regatta_H

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Regatta
