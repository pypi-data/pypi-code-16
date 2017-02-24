# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.EVT.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.EVT.Event
#
# Purpose
#    Model a calendary event
#
# Revision Dates
#    10-Mar-2010 (CT) Creation
#    16-Mar-2010 (CT) `_change_callback` added
#    18-Aug-2010 (CT) `dates.computed` changed to use `recurrence.dates`
#    18-Aug-2010 (CT) Attribute `rule` removed
#    18-Aug-2010 (CT) `recurrence` changed from `A_Recurrence_Rule` to
#                     `A_Recurrence_Rule_Set`
#     6-Sep-2010 (CT) `recurrence` changed from list of composite attributes
#                     to `Link1`
#     7-Sep-2010 (CT) `_change_callback` guarded by
#                     `date in change.attr_changes`
#     8-Sep-2010 (CT) `dates.computed` changed to use temporary
#                     `Recurrence_Rule` if not explicit one is given
#    17-Nov-2010 (CT) `left.sort_rank` set to `10` to have events sort by
#                     (`date`,`time`,`left`) instead of (`left`,`date`,`time`)
#    22-Dec-2010 (CT) `Event_occurs.electric` redefined as `Const` with `True`
#     9-Sep-2011 (CT) Use `.E_Type` instead of `._etype`
#    22-Sep-2011 (CT) s/A_Entity/A_Id_Entity/
#     8-Nov-2011 (CT) Add `calendar`, `left.completer`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    12-Sep-2012 (CT) Change `compute_occurrences` to use `sorted`
#                     (to achieve determistic test output)
#    17-Apr-2013 (CT) Use `Computed_Set_Mixin`, not `Computed_Mixin`
#    10-May-2013 (CT) Replace `auto_cache` by `link_ref_attr_name`
#     3-Aug-2013 (CT) Add guard to `Event._change_callback`
#    24-Feb-2014 (CT) Change `Event.left.role_type` to `MOM.Id_Entity`
#    24-Feb-2014 (CT) Change `Event_occurs` `Computed` attributes to `Query`
#     7-May-2014 (CT) Add `Event.left.allow_e_types` and `.refuse_e_types`
#    ««revision-date»»···
#--

from   __future__                 import print_function, unicode_literals

from   _MOM.import_MOM            import *
from   _MOM._Attr.Type            import *
from   _MOM._Attr.Date_Interval   import *
from   _MOM._Attr.Time_Interval   import *

from   _GTW                       import GTW

import _GTW._OMP._EVT.Entity
import _GTW._OMP._EVT.Calendar

from   _TFL.I18N                  import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.EVT.Link1

class Event (_Ancestor_Essence) :
    """Model a calendary event (or set of recurring events)"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Object which this event is bound to."""

            role_type          = MOM.Id_Entity
            role_name          = "object"
            link_ref_attr_name = "event"

            ### the eligible E_Types for this role are not related by
            ### inheritance:
            ### * set `refuse_e_types` to all
            ### * explicitly list `allow_e_types`
            allow_e_types      = \
                ( "PAP.Subject"
                , "SRM.Page",   "SRM.Regatta", "SRM.Regatta_Event"
                , "SWP.Clip_O", "SWP.Gallery", "SWP.Object_PN", "SWP.Page"
                )
            refuse_e_types     = ("MOM.Id_Entity", )

            ### give `date` and `time` priority for sorting
            sort_rank          = 10

            completer          = Attr.E_Completer_Spec (Attr.Selector.primary)

        # end class left

        class date (A_Date_Interval) :
            """Date interval of event (for non-recurring events, only `start` is relevant)"""

            kind               = Attr.Primary_Optional

        # end class date

        class time (A_Time_Interval) :
            """Time interval of event (for a full-day event, this is empty)"""

            kind               = Attr.Primary_Optional

        # end class time

        class calendar (A_Id_Entity) :
            """Calendar to which the event belongs"""

            P_Type             = GTW.OMP.EVT.Calendar
            kind               = Attr.Primary_Optional
            completer          = Attr.E_Completer_Spec ()
            ui_allow_new       = False

        # end class calendar

        ### Non-primary attributes

        class dates (A_Blob) :

            kind               = Attr.Computed

            def computed (self, obj) :
                rr = obj.recurrence
                if not rr :
                    if not obj.date :
                        return []
                    ### create temporary Recurrence_Spec and Recurrence_Rule
                    ### without putting them into `home_scope`
                    scope = obj.home_scope
                    rs = scope.EVT.Recurrence_Spec.E_Type (obj, scope = scope)
                    rr = scope.EVT.Recurrence_Rule.E_Type (rs,  scope = scope)
                return list (rr.occurrences)
            # end def computed

        # end class dates

        class detail (A_String) :
            """Information about event."""

            kind               = Attr.Optional
            max_length         = 160

        # end class detail

        class short_title (A_String) :
            """Short title (used in navigation)."""

            kind               = Attr.Optional
            max_length         = 30

        # end class short_title

    # end class _Attributes

    def compute_occurrences (self) :
        scope = self.home_scope
        ETM   = self.home_scope ["GTW.OMP.EVT.Event_occurs"]
        for o in sorted (self.occurs, key = TFL.Getter.pid) :
            o.destroy ()
        for d in self.dates :
            ETM (self, date = d, time = self.time)
    # end def compute_occurrences

    @classmethod
    def _change_callback (cls, scope, change) :
        if "date" in change.attr_changes or isinstance \
               (change, MOM.SCM.Change.Create):
            self = change.entity (scope)
            if self is not None :
                self.compute_occurrences ()
            else :
                print \
                    ( "No entity found for %s change-callback for change %s"
                    % (cls, change)
                    )
    # end def _change_callback

# end class Event

MOM.SCM.Change.Create.add_callback         (Event, Event._change_callback)
MOM.SCM.Change.Attr.add_callback           (Event, Event._change_callback)

_Ancestor_Essence = GTW.OMP.EVT.Link1

class Event_occurs (_Ancestor_Essence) :
    """Occurrence of a calendary event."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Event that occurs"""

            role_type          = Event
            role_name          = "event"
            link_ref_attr_name = "occurs"
            link_ref_suffix    = None     ### disable automatic pluralization

            ### give `date` and `time` priority for sorting
            sort_rank          = 10

        # end class left

        class date (A_Date) :
            """Date of occurrence"""

            kind               = Attr.Primary

        # end class date

        class time (A_Time_Interval) :
            """Time (interval) of occurrence"""

            kind               = Attr.Primary_Optional

        # end class time

        ### Non-primary attributes

        class detail (A_String) :

            kind               = Attr.Query
            max_length         = 160
            query              = Q.event.detail

        # end class detail

        class electric (_Ancestor.electric) :

            kind       = Attr.Const
            default    = True

        # end class electric

        class essence (_A_Id_Entity_) :

            kind               = Attr.Query
            query              = Q.event.object

        # end class essence

        class short_title (A_String) :

            kind               = Attr.Query
            max_length         = 30
            query              = Q.event.short_title

        # end class short_title

    # end class _Attributes

# end class Event_occurs

if __name__ != "__main__" :
    GTW.OMP.EVT._Export ("*")
### __END__ GTW.OMP.EVT.Event
