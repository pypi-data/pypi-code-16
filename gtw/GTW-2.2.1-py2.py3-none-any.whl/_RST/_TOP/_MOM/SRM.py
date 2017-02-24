# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.MOM.SRM
#
# Purpose
#    Archive of pages displaying regattas
#
# Revision Dates
#    18-Jul-2012 (CT) Creation
#    26-Jul-2012 (CT) Add `Archive.Year.regattas`
#     6-Aug-2012 (CT) Replace `_do_change_info_skip` by `skip_etag`
#    10-Aug-2012 (CT) Add missing `SRM.` to `change_query_filters`
#    10-Aug-2012 (CT) Add `skip_etag` to various classes
#    17-Sep-2012 (CT) Add `is_cancelled` to `Regatta_Event.sort_key`
#     6-Nov-2012 (CT) Add `href_regatta` to `Archive`
#    12-Nov-2012 (CT) Redefine `Regatta._get_child` to return `admin`
#                     factor `_get_bir_admin` for use by `_get_child`
#     5-Dec-2012 (CT) Add `Regatta_Event.regattas`
#     5-Dec-2012 (CT) Fix typo in `Archive.Year.regattas`
#     5-Dec-2012 (CT) Redefine `Archive.Year.sort_key`
#     7-Dec-2012 (CT) Rename `query_filters` to `query_filters_d`
#    17-Mar-2013 (CT) Add `_login_required = False` to `_get_bir_admin`
#     3-May-2013 (CT) Rename `login_required` to `auth_required`
#     4-May-2013 (CT) Add `submit_error_callback`,
#                     factor methods from `_register_submit_callback`
#    23-May-2013 (CT) Add `_regatta_registration_changed_msg`, call it in
#                     `_register_submit_error_callback`
#    14-Jun-2013 (CT) Add CSV-rendering for `Regatta.Registration`
#    15-Jun-2013 (CT) Add guard to CSV-rendering against empty `boats`
#    16-Jan-2014 (CT) Use `MOM.formatted`, not home-grown code, for
#                     registration email
#    13-Feb-2014 (CT) Use `object_entries` for `Archive.Year.regattas`
#    25-Jun-2014 (CT) Redefine `_add_other_entries` to call
#                     `_add_referral_entries`
#    30-Aug-2014 (CT) Change `_regatta_registration_formatted` for MF3 forms
#    30-Aug-2014 (CT) Factor `_formatted_submit_elements`
#    30-Aug-2014 (CT) Apply `pyk.decoded` to result of `formatted`
#     2-Feb-2015 (CT) Add and use `Renderer` for `_Regatta_Page_`
#     5-Feb-2015 (CT) Factor `_Regatta_Mixin_`
#     6-Feb-2015 (CT) Factor `can_register`
#    10-Feb-2015 (CT) Factor `fields_default`, `template_iter`,
#                     `_handle_method_context` to `Renderer_Mixin`
#    10-Feb-2015 (CT) Use `Renderer` for `Archive.Year`
#    11-Mar-2015 (CT) Remove check for `bir_admin` from `can_register`
#                     * otherwise, register buttons aren't visible before
#                       somebody visits the `bir_admin`
#    11-Mar-2015 (CT) Add `register` to `Regatta`
#    16-Apr-2015 (CT) Factor `mf3_attr_spec_r`
#     6-May-2015 (CT) Add "boat.b_class" to `Registration.list_display`
#    22-Jun-2015 (CT) Add `sort_key` for `_crew` fields
#    21-Sep-2015 (CT) Add `_real_name` to `Renderer` classes
#    21-Sep-2015 (CT) Add permission `Can_Register`
#    22-Oct-2015 (CT) Make `_response_body_csv` Python-3 compatible
#                     (use `pyk.as_str (s)`, not `pyk.text_type (s).encoded`)
#    24-May-2016 (CT) Add `sorted` to `Field_Regatta_Kinds`;
#                     Use `Is cancelled`, not `Cancelled` as text for cancelled
#                     regattas (L10N)
#     4-Jan-2017 (CT) Add `bir_admin` guard to `Regatta._get_child`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

from   _GTW._RST.Permission     import Is_Superuser

import _GTW._RST._TOP.import_TOP
import _GTW._RST._TOP._MOM.import_MOM

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Property      import Alias_Property
from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import first, uniq
from   _TFL.pyk                 import pyk

import _TFL.defaultdict

from   posixpath                import join as pp_join

import datetime
import itertools

class Can_Register (GTW.RST._Permission_) :
    """Permission for regatta registration."""

    auth_required = False

    def message (self, user, page, * args, ** kw) :
        obj = page.parent.obj
        if obj.is_cancelled :
            fmt = _T ("Regatta %s is cancelled")
        else :
            fmt = _T ("Registration for %s is closed")
        return fmt % (obj.ui_display, )
    # end def message

    def predicate (self, user, page, * args, ** kw) :
        return page.can_register
    # end def predicate

# end class Can_Register

class Is_Skipper (GTW.RST._User_Person_Matches_Attribute_) :
    """Permission if user matches the skipper"""

    attr_name = "skipper.person"

# end class Is_Crew_Request_Owner

class _Regatta_Page_ \
        ( GTW.RST.TOP.MOM.Renderer_Mixin
        , GTW.RST.TOP.MOM.Entity_Mixin_Base
        , GTW.RST.TOP.Page
        ) :

    nav_off_canvas                = True
    skip_etag                     = True

    page_template_name            = "regatta_page_r"

    _field_class_map              = dict \
        ( { "boat.sail_number"    : "Sail-Number"
          , "boat.sail_number_x"  : "Sail-Number-X"
          }
        , place                   = "Place"
        , points                  = "Points"
        , race_results            = "Race-Result"
        , registration_date       = "Date"
        , skipper_crew_club       = "Club"
        , skipper_crew_mna_number = "MNA-Number"
        , skipper_crew_person     = "Crew"
        , team_table              = "Team"
        )

    _field_pred_map               = dict \
        ( { "boat.b_class"        : Q.obj.handicap
          , "boat.sail_number_x"  : Q.obj.handicap
          }
        )

    _field_type_map               = dict \
        ( { "boat.b_class"        : Q.Field_Boat_Class
          , "boat.nation"         : Q.Field_Boat_Nation
          , "boat.sail_number_x"  : Q.Field_Boat_Sail_Number_X
          }
        , boat_sail_number        = Q.Field_Boat
        , boat_index              = GTW.RST.TOP.MOM.Field.Index
        , index                   = GTW.RST.TOP.MOM.Field.Index
        , race_results            = Q.Field_Race_Results
        , skipper_crew_club       = Q.Field_Skipper_Crew_Club
        , skipper_crew_mna_number = Q.Field_Skipper_Crew_MNA_Number
        , skipper_crew_person     = Q.Field_Skipper_Crew_Person
        , team_table              = Q.Field_Team_Table
        , _crew_club              = Q.Field__Crew_Club
        , _crew_mna_number        = Q.Field__Crew_MNA_Number
        , _crew_person            = Q.Field__Crew_Person
        , _crew_person_set        = Q.Field__Crew_Person_Set
        , _skipper_person         = Q.Field__Skipper_Person
        )

    class _Field_Person_Attr_Set_ \
            (GTW.RST.TOP.MOM.Field.AQ, GTW.RST.TOP.MOM.Field.Attr_Set_1) :

        ### Normally, a plain GTW.RST.TOP.MOM.Field.AQ would be good enough
        ### for an attribute referring to a `PAP.Person` instance, but
        ### `PAP.Person.ui_display` includes `title` which isn't appropriate
        ### in a sailing regatta according to Markus Kerschbaum

        attr_names = ("last_name", "first_name", "middle_name")

    # end class _Field_Person_Attr_Set_

    class Field_Boat (GTW.RST.TOP.MOM.Field.Attr_Set_M) :

        attr_names = ("boat.nation", "boat.sail_number_x", "boat.sail_number")

        @property ### depends on currently selected language (I18N/L10N)
        @getattr_safe
        def ui_name (self) :
            return _T ("Sail-No.")
        # end def ui_name

    # end class Field_Boat

    class Field_Boat_Class (GTW.RST.TOP.MOM.Field.AQ) :

        css_class_add = "Boat-Class"

        @property ### depends on currently selected language (I18N/L10N)
        @getattr_safe
        def ui_name (self) :
            return _T ("Class")
        # end def ui_name

    # end class Field_Boat_Class

    class Field_Boat_Nation (GTW.RST.TOP.MOM.Field.AQ) :

        css_class_add = "Nation"

        def value (self, o, renderer) :
            if isinstance (o, MOM.Id_Entity) :
                o  = o.FO
            snx = o.boat.sail_number_x
            result = snx if snx and snx.upper () != "X" else o.boat.nation
            return result
        # end def value

    # end class Field_Boat_Nation

    class Field_Boat_Sail_Number_X (GTW.RST.TOP.MOM.Field.AQ) :

        def value (self, o, renderer) :
            if isinstance (o, MOM.Id_Entity) :
                o  = o.FO
            snx    = o.boat.sail_number_x
            result = "&nbsp;X" if snx and snx.upper () == "X" else ""
            return result
        # end def value

    # end class Field_Boat_Sail_Number_X

    class Field__Crew_Club (GTW.RST.TOP.MOM.Field.Id_Entity_Set) :

        attr_name  = "_crew"
        attr_names = ("club", )
        sort_key   = TFL.Sorted_By ("key", "pid")

    # end class Field__Crew_Club_

    class Field__Crew_MNA_Number (GTW.RST.TOP.MOM.Field.Id_Entity_Set) :

        attr_name  = "_crew"
        attr_names = ("mna_number", )
        sort_key   = TFL.Sorted_By ("key", "pid")

    # end class Field__Crew_MNA_Number

    class Field__Crew_Person (GTW.RST.TOP.MOM.Field.Id_Entity_Set) :

        attr_name  = "_crew"
        attr_names = ("_crew_person_set", )
        sort_key   = TFL.Sorted_By ("key", "pid")

    # end class Field__Crew_Person

    class Field__Crew_Person_Set (_Field_Person_Attr_Set_) :

        attr_name  = "person"

    # end class Field__Crew_Person_Set

    class Field_Race_Result  (GTW.RST.TOP.MOM.Field.Base) :

        attr_name     = "race_results"
        css_class_add = "Race-Result"

        @Once_Property
        def ui_name (self) :
            return str (self.field_name + 1)
        # end def ui_name

        def as_html (self, o, renderer) :
            return "<br>".join (self.as_html_iter (o, renderer))
        # end def as_html

        def as_html_iter (self, o, renderer) :
            value = self.value (o, renderer)
            FO    = value.FO
            yield FO.points
            if value.status :
                yield FO.status
        # end def as_html_iter

        def css_class_dyn (self, o, renderer) :
            result = self.__super.css_class_dyn (o, renderer)
            value  = self.value (o, renderer)
            if value.discarded :
                result = " ".join ((result, "discarded"))
            return result
        # end def css_class_dyn

        def value (self, o, renderer) :
            result = self._value_getter (o)
            return result [self.field_name]
        # end def value

    # end class Field_Race_Result

    class Field_Race_Results (GTW.RST.TOP.MOM.Field.AQ) :

        @Once_Property
        @getattr_safe
        def fields (self) :
            resource = self.resource
            Field    = resource.Field_Race_Result
            P_Type   = self.P_Type
            result   = tuple \
                (   Field (resource, i, P_Type)
                for i in range (resource.regatta.races)
                )
            return result
        # end def fields

        @Once_Property
        @getattr_safe
        def P_Type (self) :
            return self.attr.P_Type
        # end def P_Type

        @property
        def td_cols (self) :
            return self.fields
        # end def td_cols

        @property
        def th_cols (self) :
            return self.fields
        # end def th_cols

        @property
        def th_cols0 (self) :
            """Per default, a field has no header column 0"""
            return (self, )
        # end def th_cols0

        @property ### depends on currently selected language (I18N/L10N)
        @getattr_safe
        def ui_name (self) :
            return _T ("Race")
        # end def ui_name

    # end class Field_Race_Results

    class _Field_Skipper_Crew_ (GTW.RST.TOP.MOM.Field.Attr_Set_R) :

        tag_set    = "ul"
        tag_item   = "li"

    # end class _Field_Skipper_Crew_

    class Field_Skipper_Crew_Club (_Field_Skipper_Crew_) :

        attr_names = ("skipper.club", "_crew_club")

        @property ### depends on currently selected language (I18N/L10N)
        @getattr_safe
        def ui_name (self) :
            return _T ("Club")
        # end def ui_name

    # end class Field_Skipper_Crew_Club

    class Field_Skipper_Crew_MNA_Number (_Field_Skipper_Crew_) :

        attr_names = ("skipper.mna_number", "_crew_mna_number")

        @property ### depends on currently selected language (I18N/L10N)
        @getattr_safe
        def ui_name (self) :
            return _T ("MNA-Number")
        # end def ui_name

    # end class Field_Skipper_Crew_MNA_Number

    class Field_Skipper_Crew_Person (_Field_Skipper_Crew_) :

        attr_names = ("_skipper_person", "_crew_person")

        @property ### depends on currently selected language (I18N/L10N)
        @getattr_safe
        def ui_name (self) :
            regatta = self.resource.obj
            result  = _T ("Sailor") if regatta.max_crew == 1 \
                else  _T ("Skipper/Crew")
            return result
        # end def ui_name

    # end class Field_Skipper_Crew_Person

    class Field__Skipper_Person (_Field_Person_Attr_Set_) :

        attr_name  = "skipper.person"

    # end class Field__Skipper_Person

    class Field_Team_Table (GTW.RST.TOP.MOM.Field.AQ) :

        attr_name  = "name"

        def as_html (self, o, renderer) :
            boats    = \
               [   renderer.etr.Instance (renderer, b, i)
               for i, b in enumerate (sorted (o.boats, key = Q.rank), 1)
               ]
            resource = self.resource
            renderer = resource.renderer
            template = resource.Templateer.get_template \
                (renderer.template_module)
            return template.call_macro \
                ("Field_Team_Table", renderer, o, boats, resource.boat_fields)
            return result
        # end def as_html

    # end class Field_Team_Table

    class _Regatta_Page__Renderer_ (GTW.RST.TOP.MOM.Renderer.E_Type) :

        _real_name          = "Renderer"
        template_module     = "ETR_table_regatta"

    Renderer = _Regatta_Page__Renderer_ # end class

    @Once_Property
    def E_Type (self) :
        result = self.scope.SRM.Boat_in_Regatta.E_Type
        ### XXX change MOM rev-ref autogeneration to do this automatically
        result.attr_prop ("race_results").attr.sort_key = TFL.Sorted_By ("race")
        return result
    # end def E_Type

    @property
    def objects (self) :
        return sorted (self.obj.boats, key = self.boat_sort_key)
    # end def objects

# end class _Regatta_Page_

class _Register_Action_ (GTW.RST.TOP.MOM.Action.Create) :

    _real_name      = "Register"
    description     = _ ("Register for regatta %(tn)s")

    @property
    @getattr_safe
    def description (self) :
        regatta = self.resource.regatta
        return _T ('Register %s for %s') % \
            (regatta.short_title, regatta.event.short_title)
    # end def description

    @Once_Property
    @getattr_safe
    def href (self) :
        return self.resource.href_register ()
    # end def href

# end class _Register_Action_

class _Registration_Page_ (_Regatta_Page_) :

    child_permission_map      = dict \
        ( change              = Is_Skipper   () | Is_Superuser ()
        , create              = Can_Register ()
        , delete              = Is_Skipper   () | Is_Superuser ()
        )

    class _Registration_Page_GET_ (_Regatta_Page_.GET) :

        _real_name      = "GET"
        _renderers      = _Regatta_Page_.GET._renderers + \
            (GTW.RST.Mime_Type.CSV, )

        def _response_body (self, resource, request, response) :
            if response.renderer and response.renderer.name == "CSV" :
                returner = self._response_body_csv
            else :
                returner = self.__super._response_body
            return returner (resource, request, response)
        # end def _response_body

        def _response_body_csv (self, resource, request, response) :
            def conv (s) :
                return pyk.as_str (s)
            boats    = resource.obj.boats
            if not boats :
                return {}
            max_crew = max (len (b.crew) for b in boats)
            b_names  = \
                [ "registration_date"
                , "nation"
                , "sailnumber"
                , "boat_class"
                ]
            c_names  = ["first_name", "last_name", "club", "oesv_no"]
            s_names  = list (".".join (["skipper", c]) for c in c_names)
            s_len    = len (s_names)
            w_names  = list \
                (   ".".join (["crew", str (i), c])
                for i in range (1, max_crew+1) for c in c_names
                )
            names    = list (itertools.chain (b_names, s_names, w_names))
            print ("*" * 5, max_crew, names)
            rows     = []
            result   = dict (names = names, rows = rows)
            for b in boats :
                row  = dict \
                    ( registration_date = b.FO.registration_date
                    , nation            = b.boat.FO.nation
                    , sailnumber        = b.boat.FO.sail_number
                    , boat_class        = b.boat.FO.b_class
                    )
                row.update (self._crew_attrs (s_names, b.skipper))
                for i, c in enumerate (b.crew) :
                    off = s_len * i
                    row.update (self._crew_attrs (w_names [off:], c))
                rows.append \
                    ( TFL.defaultdict
                        (str, ((k, conv (v)) for k, v in row.items ()))
                    )
            return result
        # end def _response_body_csv

        def _crew_attrs (self, names, crew) :
            return dict \
                ( zip
                    ( names
                    , [ crew.FO.person.first_name
                      , crew.FO.person.last_name
                      , crew.FO.club
                      , crew.FO.mna_number or ""
                      ]
                    )
                )
        # end def _crew_attrs

    GET = _Registration_Page_GET_ # end class

    class _Registration_Page_Renderer_ (_Regatta_Page_.Renderer) :

        _real_name           = "Renderer"

        _Actions_I           = \
            ( GTW.RST.TOP.MOM.Action.Change
            , GTW.RST.TOP.MOM.Action.Delete
            )
        Actions_T           = (_Register_Action_, )
        css_classes         = ("Registration", )
        template_module     = "ETR_table_regatta_register"

        @property
        @getattr_safe (default = ())
        def Actions_I (self) :
            if self.resource.can_register :
                user = self.resource.user
                if user and user.superuser :
                    return self._Actions_I
            return ()
        # end def Actions_I

        @property
        @getattr_safe (default = ())
        def actions_at_top (self) :
            if self.resource.can_register :
                return self.__super.actions_at_top
        # end def actions_at_top

        @property
        @getattr_safe (default = ())
        def actions_at_bottom (self) :
            if self.resource.can_register :
                return self.__super.actions_at_bottom
        # end def actions_at_bottom

    Renderer = _Registration_Page_Renderer_ # end class

    boat_sort_key = TFL.Sorted_By \
        ( "skipper.person.last_name"
        , "skipper.person.first_name"
        , "boat.sail_number"
        )

# end class _Registration_Page_

class _Result_Page_ (_Regatta_Page_) :

    class _Result_Page_Renderer_ (_Regatta_Page_.Renderer) :

        _real_name          = "Renderer"
        css_classes         = ("Result", )
        template_module     = "ETR_table_regatta_result"

    Renderer = _Result_Page_Renderer_ # end class

    boat_sort_key = Q.place

# end class _Result_Page_

class _Teamrace_Mixin_ (_Regatta_Page_) :

    @Once_Property
    def boat_fields (self) :
        E_Type = self.scope.SRM.Boat_in_Regatta.E_Type
        return self._fields (self.boat_attr_names, E_Type = E_Type)
    # end def boat_fields

    @Once_Property
    def E_Type (self) :
        result = self.scope.SRM.Team.E_Type
        return result
    # end def E_Type

    @property
    def objects (self) :
        return sorted (self.regatta.teams, key = self.team_sort_key)
    # end def objects

# end class _Teamrace_Mixin_

class _Regatta_Mixin_ (GTW.RST.TOP.MOM.Entity_Mixin_Base) :

    bir_admin               = None
    register_email_template = "regatta_register_email"
    skip_etag               = True

    class Registration (_Registration_Page_) :

        list_display        = \
            ( "boat_index"
            , "boat.b_class"
            , "boat_sail_number"
            , "skipper_crew_person"
            , "skipper_crew_club"
            , "skipper_crew_mna_number"
            , "registration_date"
            )

    # end class Registration

    class Registration_Teamrace (_Teamrace_Mixin_, _Registration_Page_) :

        class Registration_Teamrace_Renderer (_Registration_Page_.Renderer) :

            _real_name      = "Renderer"
            css_classes     = ("Registration", "Teamrace")

        Renderer = Registration_Teamrace_Renderer # end class

        boat_attr_names     = \
            ( "boat_index"
            , "boat_sail_number"
            , "skipper_crew_person"
            , "skipper_crew_club"
            , "skipper_crew_mna_number"
            )

        list_display        = \
            ( "index"
            , "team_table"
            )

        page_template_name  = "regatta_page_r"
        team_sort_key       = Q.pid

    # end class Registration_Teamrace

    class Result (_Result_Page_) :

        list_display        = \
            ( "place"
            , "boat_sail_number"
            , "skipper_crew_person"
            , "skipper_crew_club"
            , "boat.b_class"
            , "points"
            , "race_results"
            )

    # end class Result

    class Result_Teamrace (_Teamrace_Mixin_, _Result_Page_) :

        class Result_Teamrace_Renderer (_Result_Page_.Renderer) :

            _real_name      = "Renderer"
            css_classes     = ("Result", "Teamrace")

        Renderer = Result_Teamrace_Renderer # end class

        boat_attr_names     = \
            ( "boat_sail_number"
            , "skipper_crew_person"
            , "skipper_crew_club"
            )

        list_display        = \
            ( "place"
            , "team_table"
            )

        team_sort_key       = Q.place

    # end class Result_Teamrace

    @property
    @getattr_safe
    def can_register (self) :
        obj = self.obj
        if not obj.is_cancelled :
            event = obj.event
            start = event.date.start
            now   = event.__class__.date.start.now ()
            if now < start :
                return True
    # end def can_register

    @Once_Property
    @getattr_safe
    def change_query_filters (self) :
        pid    = self.obj.pid
        rq     = self.ETM_BiR.query (Q.right == pid).attr ("pid")
        result = (Q.OR (Q.pid.IN (rq), Q.pid == pid), )
        return result
    # end def change_query_filters

    @property
    @getattr_safe
    def entries (self) :
        cid = self._changed_cid ()
        if cid is not None or not self._entries :
            self._old_cid   = cid
            self._entries   = []
            self._entry_map = {}
            pages = self._get_pages ()
            self.add_entries (* pages)
        return self._entries
    # end def entries

    @Once_Property
    def ETM_BiR (self) :
        return self.scope.SRM.Boat_in_Regatta
    # end def ETM_BiR

    @property
    @getattr_safe
    def mf3_attr_spec_r (self) :
        """Attribute specification for MF3 form instance for registration"""
        obj    = self.obj
        scope  = self.scope
        result = dict (right = dict (default = obj))
        if isinstance (obj, scope.SRM.Regatta_C.E_Type) :
            b_class    = obj.boat_class
            max_rr     = b_class.max_crew - 1
            result.update \
                ( { "left.left"     : dict
                    ( prefilled     = True
                    , default       = b_class
                    )
                  }
                , _crew             = dict
                    ( max_rev_ref   = max_rr
                    , min_rev_ref   = 1 if max_rr else 0
                    )
                , yardstick         = dict
                    ( skip          = True
                    )
                )
        return result
    # end def mf3_attr_spec

    def href_change (self, obj) :
        if self.bir_admin :
            return self.bir_admin.href_change (obj)
    # end def href_change

    def href_delete (self, obj) :
        if self.bir_admin :
            return self.bir_admin.href_delete (obj)
    # end def href_delete

    def href_register (self) :
        obj = self.obj
        if self.can_register :
            if not obj.is_team_race :
                return pp_join (self.abs_href_dynamic, "register")
            ### XXX implement registration for team race, too
    # end def href_register

    def _get_bir_admin (self) :
        bir    = self.top.ET_Map ["SRM.Boat_in_Regatta"]
        result = self.bir_admin
        if result is None and bir and bir.admin :
            UIS    = self.scope.SRM.Boat_in_Regatta.UI_Spec
            kw     = dict \
                ( bir.admin._orig_kw
                , child_permission_map  =
                    _Registration_Page_.child_permission_map
                , default_qr_kw         = dict (right___EQ = self.obj.pid)
                , MF3_Attr_Spec         = UIS ["MF3_Attr_Spec_R"]
                , MF3_Form_Spec         = UIS ["MF3_Form_Spec_R"]
                , mf3_attr_spec         = self.mf3_attr_spec_r
                , mf3_id_prefix         = "BiR_R"
                , implicit              = True
                , name                  = "admin"
                , parent                = self
                , submit_callback       = self._register_submit_callback
                , submit_error_callback = self._register_submit_error_callback
                , _auth_required        = False
                )
            result = self.bir_admin = bir.admin.__class__ (** kw)
        return result
    # end def _get_bir_admin

    def _regatta_registration_changed_msg (self, resource, scope, fv) :
        return resource._formatted_submit_elements (scope, fv)
    # end def _regatta_registration_changed_msg

    def _regatta_registration_formatted (self, resource, scope, fv) :
        skip = set (["right", "_crew.key"])
        return resource._formatted_submit_entities (scope, fv, skip)
    # end def _regatta_registration_formatted

    def _register_submit_callback (self, resource, request, response, scope, fv, result) :
        message = self._regatta_registration_formatted (resource, scope, fv)
        self._send_registration_email \
            (resource, request, response, scope, fv, result, message)
    # end def _register_submit_callback

    def _register_submit_error_callback (self, resource, request, response, scope, fv, result) :
        from _TFL.formatted_repr import formatted_repr as formatted
        errors    = pyk.decoded \
            ("\n\n".join (formatted (e) for e in fv.errors))
        message = "\n\n-----------------\n\n".join \
            (( self._regatta_registration_formatted   (resource, scope, fv)
             , errors
             , self._regatta_registration_changed_msg (resource, scope, fv)
            ))
        self._send_registration_email \
            ( resource, request, response, scope, fv, result, message
            , "*** failed ***"
            )
    # end def _register_submit_error_callback

    def _send_registration_email \
            ( self, resource, request, response, scope, fv, result, message
            , subject_tail = ""
            ):
        try :
            email = self.email_from
            self.send_email \
                ( self.register_email_template
                , email_from    = email
                , email_to      = email
                , email_subject = _T ("%s: regatta registration %s")
                      % (self.obj.ui_display, subject_tail)
                , message       = message
                , NAV           = self.top
                , page          = self
                , request       = request
                )
        except Exception as exc :
            pyk.fprint \
                ( "Sending regatta registration email to %r failed "
                  "with exception %s"
                % (email, exc)
                )
            pyk.fprint (message)
    # end def _send_registration_email

# end class _Regatta_Mixin_

_Ancestor = GTW.RST.TOP.Dir

class Regatta (_Regatta_Mixin_, _Ancestor) :
    """Directory displaying a regatta."""

    def _add_other_entries (self) :
        self._add_referral_entries      ()
        self.__super._add_other_entries ()
    # end def _add_other_entries

    def _get_child (self, child, * grandchildren) :
        result = self.__super._get_child (child, * grandchildren)
        if result is None :
            if child == "admin" :
                result = self._get_bir_admin ()
                if result :
                    _entries = self._entries
                    if ((not _entries) or _entries [-1] is not result) :
                        self.add_entries (result)
                    if grandchildren :
                        result = result._get_child (* grandchildren)
            elif child == "register" :
                bir_admin = self._get_bir_admin ()
                if bir_admin is not None :
                    result = GTW.RST.TOP.Alias \
                        ( name          = child
                        , hidden        = True
                        , parent        = self
                        , short_title   = child
                        , target        = bir_admin._get_child ("create")
                        , title         =
                            ( _T ("Register an entry for %s at %s")
                            % (self.short_title, self.parent.short_title)
                            )
                        )
        return result
    # end def _get_child

    def _get_pages (self) :
        np     = _T ("Participants")
        nr     = _T ("Results")
        obj    = self.obj
        result = []
        scope  = self.scope
        sk     = TFL.Sorted_By \
            ("skipper.person.last_name", "skipper.person.first_name")
        Result_Type = None
        if obj.is_team_race :
            Registration_Type = self.Registration_Teamrace
            try :
                place = first (obj.teams).place
            except IndexError :
                pass
            else :
                if place :
                    Result_Type = self.Result_Teamrace
        else :
            Registration_Type = self.Registration
            if obj.races :
                Result_Type = self.Result
        if Result_Type :
            result.append \
                ( Result_Type
                    ( ETM         = obj.ETM
                    , name        = nr.lower ()
                    , obj         = obj
                    , parent      = self
                    , regatta     = obj
                    , short_title = nr
                    , title       = "%s %s" %
                        ( _T ("Results for"), self.short_title)
                    )
                )
        head = _T ("List of participants for")
        result.append \
            ( Registration_Type
                ( ETM         = obj.ETM
                , head_line   = "%s %s<br />%s, %s" %
                    ( _T ("Registration list"), obj.name
                    , obj.event.FO.short_title, obj.event.ui_date
                    )
                , name        = np.lower ()
                , nav_off_canvas = False
                , obj         = obj
                , parent      = self
                , regatta     = obj
                , short_title = np
                , title       = "%s %s" % (head, self.short_title)
                )
            )
        bir_admin = self._get_bir_admin ()
        if bir_admin :
            result.append (bir_admin)
        return result
    # end def _get_pages

# end class Regatta

_Ancestor = GTW.RST.TOP.Dir

class Regatta_Event \
          ( GTW.RST.TOP.MOM.Entity_Mixin_Base
          , GTW.RST.TOP.MOM.E_Type_Mixin
          , _Ancestor
          ) :
    """Directory displaying a regatta event."""

    Entity              = Regatta

    dir_template_name   = None
    page_template_name  = "regatta_page"
    skip_etag           = True
    sort_key            = TFL.Sorted_By \
        ("is_cancelled", Q.races == 0, "perma_name")

    _old_date           = None

    class Page (GTW.RST.TOP.MOM.Display.Entity) :

        skip_etag           = True
        page_template_name  = "regatta_page"

    # end class Page

    def __init__ (self, ** kw) :
        kw ["ETM"] = "SRM.Regatta"
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    @getattr_safe
    def ETM_P (self) :
        return self.top.scope.SRM.Page
    # end def ETM_P

    @Once_Property
    @getattr_safe
    def change_query_filters (self) :
        pid    = self.obj.pid
        pq     = self.ETM_P.query (Q.event == pid).attr ("pid")
        rq     = self.ETM.query   (Q.left  == pid).attr ("pid")
        result = (Q.OR (Q.pid.IN (rq), Q.pid.IN (pq)), )
        return result
    # end def change_query_filters

    @property
    @getattr_safe
    def entries (self) :
        today = datetime.date.today ()
        if today == self._old_date :
            _old_entries    = self._entries
        else :
            _old_entries    = None
            self._entries   = []
            self._entry_map = {}
            self._old_date  = today
        result = self.__super.entries
        if result is not _old_entries or not result :
            pages = self._get_pages ()
            if today >= self.obj.date.start :
                self.add_entries (* pages)
            else :
                result          = pages + result
                self._entries   = []
                self._entry_map = {}
                self.add_entries (* result)
        return self._entries
    # end def entries

    @property
    @getattr_safe
    def query_filters_d (self) :
        return self.__super.query_filters_d + (Q.left == self.obj.pid, )
    # end def query_filters_d

    @property
    @getattr_safe
    def regattas (self) :
        ### Cannot use `object_entries` here because some non-Regatta entries
        ### are at the front of `entries`
        return [e for e in self.entries if isinstance (e, Regatta)]
    # end def regattas

    def _add_other_entries (self) :
        self._add_referral_entries      ()
        self.__super._add_other_entries ()
    # end def _add_other_entries

    def _add_href_pat_frag_tail \
            (self, head, getter = TFL.Getter.href_pat_frag) :
        ### reduce memory consumption by not traversing into `entries`
        return head
    # end def _add_href_pat_frag_tail

    def _get_pages (self) :
        T     = self.Page
        ETM   = self.ETM_P
        pkw   = self.page_args
        kw    = dict (pkw, ETM = ETM)
        query = ETM.query_s (event = self.obj.pid)
        return \
            [T (parent = self, obj = o, page_args = pkw, ** kw) for o in query]
    # end def _get_pages

# end class Regatta_Event

_Ancestor = GTW.RST.TOP.MOM.Display.E_Type_Archive_DSY

class Archive (_Ancestor) :
    """Archive of pages displaying regatta events, organized by year."""

    class _SRM_Year_ (GTW.RST.TOP.MOM.Renderer_Mixin, _Ancestor.Year) :

        _real_name          = "Year"

        dir_template_name   = "regatta_calendar"
        Entity              = Regatta_Event
        head_line_format    = _ ("Regatta Events %(year)s")
        list_display        = \
            ( "ui_date_short"
            , "regatta_kinds"
            , "regatta_classes"
            , "event_link"
            )
        regattas            = Alias_Property ("object_entries")
        skip_etag           = True
        sort_key            = TFL.Sorted_By ("date.start", "perma_name")

        _field_class_map    = dict \
            ( ui_date_short     = "align-right"
            )

        _field_type_map     = dict \
            ( event_link            = Q.Field_Event_Link
            , regatta_classes       = Q.Field_Regatta_Classes
            , regatta_kinds         = Q.Field_Regatta_Kinds
            )

        class Field_Event_Link (GTW.RST.TOP.MOM.Field.HTML_Link) :

            attr_name = "desc"

            @property ### depends on currently selected language (I18N/L10N)
            @getattr_safe
            def ui_name (self) :
                return _T ("Regatta")
            # end def ui_name

            def _as_html_href (self, o, renderer) :
                resource = self.resource
                href     = resource.href_display (o)
                return href
            # end def _as_html_href

            def _as_html_value (self, o, renderer) :
                return o.desc
            # end def _as_html_value

        # end class Field_Event_Link

        class Field_Regatta_Classes (GTW.RST.TOP.MOM.Field.HTML_Link_Set) :

            attr_name = "regattas"

            @property ### depends on currently selected language (I18N/L10N)
            @getattr_safe
            def ui_name (self) :
                return _T ("Class")
            # end def ui_name

            def _as_html_href (self, o, renderer) :
                resource = self.resource
                regatta  = self._value_getter (o)
                href     = resource.href_regatta (regatta) \
                    if not regatta.is_cancelled else ""
                return href
            # end def _as_html_href

            def _as_html_value (self, o, renderer) :
                regatta  = self._value_getter (o)
                return regatta.name.replace (" ", " ")
            # end def _as_html_value

        # end class Field_Regatta_Classes

        class Field_Regatta_Kinds (GTW.RST.TOP.MOM.Field.AQ) :

            attr_name = "regattas"

            @property ### depends on currently selected language (I18N/L10N)
            @getattr_safe
            def ui_name (self) :
                return _T ("Kind")
            # end def ui_name

            def as_html (self, o, renderer) :
                regattas = sorted (self._value_getter (o), key = Q.name)
                canc     = _T ("Is cancelled")
                return "<br>".join \
                    ((r.kind if not r.is_cancelled else canc) for r in regattas)
            # end def as_html

        # end class Field_Regatta_Kinds

        class _SRM_Year_Renderer_ (GTW.RST.TOP.MOM.Renderer.E_Type) :

            _real_name          = "Renderer"
            template_module     = "ETR_table_regatta"

        Renderer = _SRM_Year_Renderer_ # end class

        @property ### depends on currently selected language (I18N/L10N)
        def head_line (self) :
            return self.head_line_format % TFL.Caller.Object_Scope (self)
        # end def head_line

    Year = _SRM_Year_ # end class

    def __init__ (self, ** kw) :
        kw.setdefault         ("ETM", "SRM.Regatta_Event")
        self.__super.__init__ (** kw)
        top   = self.top
        apt   = top.App_Type
        map   = top.ET_Map
        for k in ( "SRM.Page", "SRM.Regatta_C", "SRM.Regatta_H") :
            et = apt [k]
            map [et.type_name].manager = self
    # end def __init__

    def href_display (self, obj) :
        scope = self.top.scope
        comps = [self.abs_href_dynamic, str (obj.year)]
        if isinstance (obj, (scope.SRM.Page.E_Type, scope.SRM.Regatta.E_Type)) :
            comps.append (obj.event.perma_name)
        comps.append (obj.perma_name)
        return pp_join (* comps)
    # end def href_display

    href_regatta = href_display

# end class Archive

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.SRM
