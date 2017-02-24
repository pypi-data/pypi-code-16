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
#    GTW.RST.TOP.MOM.Admin
#
# Purpose
#    Directories and pages for managing instances of MOM E-types
#
# Revision Dates
#    19-Jul-2012 (CT) Creation
#    25-Jul-2012 (CT) Fix `Alias`: delegate `ETM` to `target`
#     2-Aug-2012 (CT) Use `response.renderer`, not `request.renderer`
#     6-Aug-2012 (CT) Replace `_do_change_info_skip` by `skip_etag`
#     6-Aug-2012 (MG) Consider `hidden`in  `is_current_dir`
#     9-Aug-2012 (CT) Fix `is_current_dir` (test for "/" after `startswith`)
#     9-Aug-2012 (CT) Redefine `E_Type.entries` to avoid version from mixin
#    10-Aug-2012 (CT) Use `logging.exception` instead of `print`
#    13-Aug-2012 (CT) Guard access to `Form` in `changer_injected_templates`
#    10-Oct-2012 (CT) Pass `error` positionally to `Status` classes
#    23-Oct-2012 (CT) Fix `E_Type_Alias.short_title`: `.target.ETM.type_name`
#     6-Nov-2012 (CT) Remove obsolete code
#    13-Nov-2012 (CT) Add `scope.rollback` to `_Changer_._rendered_post`
#    21-Nov-2012 (CT) Fix indentation of `scope.rollback` call
#     7-Dec-2012 (CT) Consider `dont_et_map`
#     7-Dec-2012 (CT) Convert `form_parameters` to `property` to allow
#                     redefinition
#    11-Dec-2012 (CT) Change default for `form.referrer` to `parent.abs_href`
#    12-Dec-2012 (CT) Fix call to `QR.from_request` in `QX_Completer`
#    13-Dec-2012 (CT) Handle `MOM.An_Entity` in `._rendered_post` of
#                     `Completer` and `Completed`
#    13-Dec-2012 (CT) Add argument `AQ` to `_rendered_completions`
#    14-Dec-2012 (CT) Use `child_permission_map` in `_new_child_x`
#    17-Dec-2012 (CT) Redefine `et_map_name`, remove init-code for `ET_Map`
#    17-Mar-2013 (CT) Add `_login_required` to `E_Type, `Group`, `Site``
#    17-Mar-2013 (CT) Add guard `response.renderer` to `E_Type.rendered`
#     3-Apr-2013 (CT) Move `json.etn` into `if "key"` clause of
#                     `_get_attr_filter`
#     3-Apr-2013 (CT) Factor `_get_esf_filter`, support `polymorphic_epk`
#    25-Apr-2013 (CT) Use `self.commit_scope`, not `scope.commit`
#    25-Apr-2013 (CT) Add `child_postconditions_map` to `_new_child_x`
#    25-Apr-2013 (CT) Add and use `eligible_object_restriction`
#     3-May-2013 (CT) Rename `login_required` to `auth_required`
#     4-May-2013 (CT) Add `submit_error_callback`
#     7-May-2013 (CT) Fix `Expander.rendered` for `An_Entity` elements
#     7-May-2013 (CT) Set `Deleter.argn` to `None`, not `1`
#    30-Oct-2013 (CT) Change `Group._pns_entries` to set `name` of E_Type_Alias
#    15-Jan-2014 (CT) Factor `_call_submit_callback`
#    16-Jan-2014 (CT) Add `_formatted_submit_entities`
#    20-Jan-2014 (CT) Redefine `_Changer_.head_line`
#    11-Feb-2014 (CT) Pass `response`, not `request`, to `_new_edit_session`
#    20-Feb-2014 (CT) Set `E_Type.nav_off_canvas` to True
#     3-Mar-2014 (CT) Change `Field.ui_name` to use `.aq._ui_name_T`
#                     and to add `zero-width-space`
#    11-Mar-2014 (CT) Redefine `_HTML_Action_.head_line`
#    11-Mar-2014 (CT) Add `Displayer`, modify `href_display`
#    11-Mar-2014 (CT) Factor `css_class` (from jinja); add `Field.as_html`
#    13-Mar-2014 (CT) Add `E_Type.first`, `.last`, `.next`, `.prev`
#    13-Mar-2014 (CT) Factor `_handle_method_context` from `rendered`
#    14-Apr-2014 (CT) Set `Site.pid` to `Admin`
#    17-Apr-2014 (CT) Add `_field_type_map`
#    17-Apr-2014 (CT) Change `Field.value` to handle `MOM.Id_Entity` instances
#    29-Apr-2014 (CT) Redefine `_NC_Mixin_._m_after__init__` to setup
#                     `_entry_type_map` based on `_v_entry_type_list`
#    30-Apr-2014 (CT) Factor `_NC_Mixin_._child_kw`
#     7-May-2014 (CT) Guard access to `default_child` in `_get_esf_filter`
#     8-Jul-2014 (CT) Change `Group._pns_entries` to filter duplicates
#    19-Aug-2014 (CT) Factor `ac_ui_display` to `MOM.E_Type_Manager`
#    20-Aug-2014 (CT) Factor `GTW.RST.TOP.MOM.Field`
#    20-Aug-2014 (CT) Use `MF3`, not `AFS`, forms
#    21-Aug-2014 (CT) Use `update_combined` to combine specs for MF3 forms
#    24-Aug-2014 (CT) Change `_get_attr_filter` to use `_get_form_field`,
#                     if possible, otherwise call `form.populate_new`
#    24-Aug-2014 (CT) Change `QX_Completer._rendered_post` to use
#                     `json.trigger_n`, not `json.trigger`
#    28-Aug-2014 (CT) Change `_get_attr_filter` to include `etns` in `key`
#    30-Aug-2014 (CT) Change `_formatted_submit_entities` to work with MF3 forms
#    30-Aug-2014 (CT) Add `_formatted_submit_elements`
#     1-Sep-2014 (CT) Change `E_Type_Mixin._get_child` to use
#                     `_child_kw ("change")` for `Instance`
#     1-Sep-2014 (CT) Change `_NC_Mixin_._new_child_x` to always call
#                     `_child_kw`
#     1-Sep-2014 (CT) Change `_Changer_._rendered_post` to handle commit
#                     error properly
#     2-Sep-2014 (CT) Change `_Changer_.rendered` to call
#                     `form.set_request_defaults (req_data)`,
#                     unfactor `_rendered__form` into `_Changer_.rendered`
#     3-Sep-2014 (CT) Return `elem` from `_get_attr_filter`
#     3-Sep-2014 (CT) Change `QX_Completer._rendered_post` to use
#                     `elem.restrict_completion`
#    22-Sep-2014 (CT) Catch missing `cargo` (die, spammers, die!)
#    24-Sep-2014 (CT) Factor `set_request_defaults`
#    25-Sep-2014 (CT) Add `Polisher`
#    26-Sep-2014 (CT) Use `_polished` in `Completer._rendered_post`
#    30-Oct-2014 (CT) Adapt to changes of `e_type` template macros
#    31-Oct-2014 (CT) Change `E_Type.rendered` to pass `qr_next_p`, not buttons
#    10-Dec-2014 (CT) Remove `.FO` rom `E_Type.Entity`
#    12-Dec-2014 (CT) Add `_Changer_.POST ` to call `csrf_check`
#    21-Jan-2015 (CT) Factor `E_Type._field` from `._fields`
#    22-Jan-2015 (CT) Add `Renderer`
#    27-Jan-2015 (CT) Add and use `fields_default`
#    27-Jan-2015 (CT) Factor `_field_type`, `_field_type_by_attr`
#    27-Jan-2015 (CT) Add `E_Type.template_iter`
#    29-Jan-2015 (CT) Make `Displayer.fields` compatible with `Renderer`
#     2-Feb-2015 (CT) Factor `_field` and friends from `E_Type` to
#                     `_TOP_MOM_Mixin_Base_`
#    10-Feb-2015 (CT) Factor `template_iter`, parts of `_handle_method_context`
#                     from `E_Type` to `Renderer_Mixin`
#    11-Feb-2015 (CT) Change `E_Type_Alias` to refer to `.target.ETM.ui_name_T`,
#                     not `.target.ETM.type_name`
#     2-Apr-2015 (CT) Add `feedback` to `_rendered_completions_a`
#    29-Apr-2015 (CT) Factor `record_commit_errors` to `GTW.MF3.Element.Entity`
#    28-May-2015 (CT) Add `E_Type_Mixin.href_instance`
#    29-May-2015 (CT) Factor `_rendered_delete`, add `result ["undo"]`
#    29-May-2015 (CT) Add `Undoer`, `E_Type_Mixin.href_undo`
#     1-Jun-2015 (CT) Add guard for `admin` to `_rendered_delete`
#     9-Jun-2015 (CT) Add guard for `renderer` to `_Changer_.renderer`
#    30-Jul-2015 (CT) Add argument `essence`, `picky` to `polisher`
#    31-Jul-2015 (CT) Handle `ValueError` from `polisher`
#    21-Sep-2015 (CT) Add `_real_name` to `Renderer` classes
#    17-Nov-2015 (CT) Set `static_p` to `False`
#    16-Dec-2015 (CT) Explicitly set `ETM` in `_pns_entries`
#    16-Dec-2015 (CT) Use `E_Type.UI_Spec`, not `Nav.Admin ["type_base_name"]`
#    26-Apr-2016 (CT) Add `pre_complete` guard to `Completer._rendered_post`
#     3-May-2016 (CT) Factor `Group._etype_entry`, allow strings in `etypes`
#    10-May-2016 (CT) Factor code from `_get_esf_filter` to `QR.Filter`
#    20-May-2016 (CT) Factor `_normalized_esf_json`
#     2-Jun-2016 (CT) Import `MOM.Selector`; add `esf_template_name`
#                     + set `template_macro` for `MOM.Selector.Classes`
#     3-Jun-2016 (CT) Change `_rendered_esf` to use `AQ.ESW`
#     6-Jun-2016 (CT) Change QX_Completed, QX_Completer to use `AQ.ESW`
#                     + add `_get_esf_values`
#    10-Jun-2016 (CT) Change `QX_Completed._rendered_post` to return `values`
#    10-Jun-2016 (CT) Factor `_rendered_post_esf_form`,
#                     move `html` generation there (from `_rendered_esf`)
#     8-Feb-2017 (CT) Remove redefinitions of `E_Type.first`, `.last`, `.next`,
#                     `.prev`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                     import CAL
from   _GTW                     import GTW
from   _TFL                     import TFL

import _CAL.Delta

from   _GTW._MF3                             import Element as MF3
from   _GTW._RST._TOP._MOM.Query_Restriction import  \
     ( Query_Restriction      as QR
     , Query_Restriction_Spec as QRS
     )

import _GTW._RST._TOP._MOM.Mixin
import _GTW._RST._TOP.Dir
import _GTW._RST._TOP.Page
import _GTW.FO
import _GTW.jQuery

from   _MOM.import_MOM          import MOM, Q

import _MOM.formatted
import _MOM.Selector

import _TFL._Meta.Object

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.formatted_repr      import formatted_repr as formatted
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import callable, first, uniq
from   _TFL.pyk                 import pyk
from   _TFL.update_combined     import update_combined

from   itertools                import chain as iter_chain
from   posixpath                import join  as pp_join

import logging

_Ancestor = GTW.RST.TOP.Page

class _Action_ (_Ancestor) :

    args                  = (None, )
    implicit              = True
    skip_etag             = True
    static_p              = False

    _exclude_robots       = True

    class _Action_POST_ (GTW.RST.POST) :

        _real_name             = "POST"

        def _response_body (self, resource, request, response) :
            result = resource._rendered_post (request, response)
            if result is None :
                raise resource.Status.Not_Found ()
            return result
        # end def _response_body

    POST = _Action_POST_ # end class

    @property
    @getattr_safe
    def obj (self) :
        ETM = self.ETM
        pid = self.args [0] if self.args else None
        if pid is not None :
            return ETM.pid_query (pid)
    # end def obj

    def form_instance (self, obj = None, mf3_attr_spec = {}, ** kw) :
        if obj is None :
            obj = self.obj
        attr_spec = dict (self.mf3_attr_spec, ** mf3_attr_spec)
        kw.setdefault ("_hash_fct", self.top.hash_fct)
        result = self.parent.Form \
            (self.scope, obj, attr_spec = attr_spec, ** kw)
        return result
    # end def form_instance

    def session_secret (self, request, sid) :
        try :
            return request.session.edit_session (sid)
        except request.session.Expired as exc :
            ### XXX re-authorization form (password only)
            raise self.top.Status.Request_Timeout ("%s" % (exc, ))
        except LookupError as exc :
            raise self.top.Status.Bad_Request ("Session expired: %s" % (exc, ))
    # end def session_secret

    def _check_readonly (self, request) :
        if self.top.scope.readonly : ### XXX might be out-of-date !!!
            error = \
                (_T ( "At the moment, the database is set to "
                      "readonly to allow maintenance."
                    )
                )
            raise self.top.Status.Service_Unavailable \
                ( error
                , retry_after = CAL.Date_Time_Delta (minutes = 15)
                )
    # end def _check_readonly

    def _raise_401 (self, request) :
        error = _T ("Not logged in or login-session is expired")
        raise self.top.Status.Unauthorized (error)
    # end def _raise_401

    def _raise_403 (self, request) :
        error = _T ("Not authorized for this page")
        raise self.top.Status.Forbidden (error)
    # end def _raise_403

    def _rendered_delete (self, request, response, obj) :
        self._check_readonly (request)
        scope  = self.top.scope
        etn    = obj.type_name
        uid    = obj.ui_display
        result = dict (feedback = _T ("""Object "%s" deleted""") % (uid, ))
        obj.destroy ()
        admin  = self.top.ET_Map [etn].admin
        if admin is None :
            admin = self.top.ET_Map [self.type_name].admin
        if admin is not None :
            change = scope.uncommitted_changes [-1]
            result.update \
                ( undo = dict
                    ( cid   = change.cid
                    , pid   = change.pid
                    , title = _T ("Undo deletion of object %s" % (uid, ))
                    , url   = admin.href_undo (change)
                    )
                )
        return result
    # end def _rendered_delete

# end class _Action_

_Ancestor = _Action_

class _HTML_Action_ (_Ancestor) :

    argn                  = None
    nav_off_canvas        = False

    class _HTML_Action_GET_ (_Ancestor.GET) :

        _real_name             = "GET"
        _renderers             = \
            _Ancestor.GET._renderers + (GTW.RST.Mime_Type.JSON, )

    GET = _HTML_Action_GET_ # end class

    class _HTML_Action_POST_ (_Ancestor.POST) :

        _real_name             = "POST"
        _renderers             = \
            _Ancestor.GET._renderers + (GTW.RST.Mime_Type.JSON, )

    POST = _HTML_Action_POST_ # end class

    @property
    @getattr_safe
    def head_line (self) :
        return "%s %s" % \
            (_T (self.__class__.name.capitalize ()), self.E_Type.ui_name_T)
    # end def head_line

    def form_value (self, request, json_cargo) :
        Status = self.top.Status
        try :
            sid    = json_cargo.get ("sid")
            secret = self.session_secret (request, sid)
            form   = self.form_instance  (sid = sid, session_secret = secret)
            result = form.submit         (self.scope, json_cargo)
        except Status.Request_Timeout as exc :
            raise
        except Exception as exc :
            logging.exception \
                ( "form_value: \n  submitted json:\n    %s"
                , formatted (json_cargo, 4)
                )
            raise Status.Bad_Request ("%s" % (exc, ))
        if result.conflicts :
            ### XXX needs to be changed ???
            raise self.top.Status.Conflict (conflicts = result.as_json_cargo)
        return result
    # end def form_value

# end class _HTML_Action_

_Ancestor = _Action_

class _JSON_Action_ (_Ancestor) :

    argn                 = 0
    esf_template_name    = "e_type_selector"

    ### Add `template_macro` to `MOM.Selector.Classes`
    for _c in MOM.Selector.Classes :
        if _c.macro_name :
            _c.template_macro = ", ".join ((esf_template_name, _c.macro_name))
    del _c

    class _JSON_Action_Method_ (GTW.RST.HTTP_Method) :

        _renderers             = (GTW.RST.Mime_Type.JSON, )

    # end class _JSON_Action_Method_

    class _JSON_Action_GET_ (_JSON_Action_Method_, _Ancestor.GET) :

        _real_name             = "GET"

    GET  = _JSON_Action_GET_ # end class

    class _JSON_Action_POST_ (_JSON_Action_Method_, _Ancestor.POST) :

        _real_name             = "POST"

        def _response_body (self, resource, request, response) :
            if request.json :
                resource.args = [request.json.get ("form_pid")]
            result = self.__super._response_body (resource, request, response)
            return result
        # end def _response_body

    POST = _JSON_Action_POST_ # end class

    def _get_attr_filter (self, request, json) :
        ET   = self.E_Type
        etn  = None
        elem = None
        if "key" in json :
            key  = json.key
            if "etn" in json :
                etn  = json.etn
        else :
            r_json = request.json
            if "sid" in json :
                form, elem  = self._get_form_field (request, r_json)
            else :
                form = self.Form  (self.scope)
                form.populate_new (r_json)
                elem = form [json.trigger]
            etn = elem.Entity.E_Type.type_name
            key = elem.attr.name
        if etn is not None :
            ET = self.scope [etn].E_Type
        return self.QR.Filter (ET, key), elem
    # end def _get_attr_filter

    def _get_esf_filter (self, request, json) :
        result, _ = self._get_attr_filter (request, json)
        return result
    # end def _get_esf_filter

    def _get_esf_values (self, request, json) :
        result = request.json.get ("values")
        if result is None :
            a_pat  = MOM.Attr.Querier.regexp.attr_opt
            id_sep = MOM.Attr.Querier.id_sep
            result = {}
            for k, v in pyk.itervalues (request.req_data) :
                if a_pat.match (k) :
                    name = ".".join (a_pat.name.split (id_sep))
                    if v :
                        result [name] = v
        return result
    # end def _get_esf_values

    def _get_form_field (self, request, json) :
        sid        = json.get ("sid")
        secret     = self.session_secret (request, sid)
        form       = self.form_instance  (sid = sid, session_secret = secret)
        form.populate_new (json)
        try :
            field  = form [json ["trigger"]]
        except KeyError :
            raise self.Status.Bad_Request
        form.check_sigs (json)
        return form, field
    # end def _get_form_field

    def _normalized_esf_json (self, request) :
        return TFL.Record (** request.json)
    # end def _normalized_esf_json

    def _rendered_completions (self, ETM, query, names, entity_p, json, AQ = None) :
        if entity_p :
            fct = self._rendered_completions_e
        else :
            fct = self._rendered_completions_a
        return fct (ETM, query, names, json, AQ)
    # end def _rendered_completions

    def _rendered_completions_a (self, ETM, query, names, json, AQ = None) :
        if AQ is None :
            AQ   = ETM.E_Type.AQ
        result   = dict (matches = [], partial = False)
        max_n    = self.max_completions + 1
        fs       = tuple (getattr (AQ, n).QR for n in names)
        matches  = query.attrs (* fs).limit (max_n).all ()
        n        = result ["completions"] = len (matches)
        finished = result ["finished"]    = n == 1
        if n :
            if n < max_n :
                result ["fields"]  = len    (names)
                result ["matches"] = sorted (ETM.ac_ui_display (names, matches))
            else :
                if json.trigger == json.trigger_n :
                    s_matches = query.attrs (fs [0]).limit (max_n).all ()
                    m = len (s_matches)
                    if m < max_n :
                        s_matches = \
                            ( [m [0], "..."] for m in ETM.ac_ui_display
                                (names [:1], s_matches)
                            )
                        result ["fields"]  = 1
                        result ["matches"] = sorted (s_matches)
                        result ["partial"] = True
                    else :
                        ### XXX find fewer partial matches !!!
                        result ["fields"] = 0
            if not result ["matches"] :
                result ["feedback"]  = _T ("More than %s matches" % n)
        return result
    # end def _rendered_completions_a

    def _rendered_completions_e (self, ETM, query, names, json, AQ = None) :
        result   = dict (partial = False)
        max_n    = self.max_completions + 1
        matches  = query.limit (max_n).all ()
        n        = result ["completions"] = len (matches)
        finished = result ["finished"]    = n == 1
        if n :
            if n < max_n :
                result ["fields"]  = 2
                result ["matches"] = sorted \
                    ((m.ui_display, m.pid) for m in matches)
            else :
                result = dict \
                    ( self._rendered_completions_a
                        (ETM, query, names [:1], json)
                    , ** result
                    )
                result ["partial"] = True
        return result
    # end def _rendered_completions_e

    def _rendered_esf (self, af, ** kw) :
        ESW           = kw.pop ("ESW", af.AQ.ESW)
        result        = dict (kw)
        selected_type = getattr (ESW, "selected_type", None)
        if selected_type is not None :
            result ["selected_type"] = selected_type
        return result
    # end def _rendered_esf

    def _rendered_post_esf_form (self, request, response) :
        json          = self._normalized_esf_json (request)
        af            = self._get_esf_filter      (request, json)
        aq            = af.AQ
        template      = self.top.Templateer.get_template ("e_type_selector")
        result        = self._rendered_esf \
            ( af
            , html    = template.call_macro ("form", self, aq, aq.ESW)
            )
        return result
    # end def _rendered_post_esf_form

# end class _JSON_Action_

class _JSON_Action_PO_ (_JSON_Action_) :

    GET = None

    def _polished (self, request, response, form, field, json, values) :
        elems   = dict   ((k, form [k]) for k in values)
        fids    = sorted (elems)
        v_dict  = dict   ((e.attr.name, values [k]) for k, e in elems.items ())
        p_dict  = field.polisher \
            ( field.attr, v_dict
            , essence = field.id_essence
            , picky   = False
            )
        result  = dict \
            ( field_ids    = fids
            , field_values = list
                (p_dict.get (elems [k].attr.name) for k in fids)
            )
        return result
    # end def _polished

# end class _JSON_Action_PO_

_Ancestor = _HTML_Action_

class _Changer_ (_Ancestor) :

    page_template_name   = "e_type_mf3"

    class _Changer__POST_ (_Ancestor.POST, GTW.RST.TOP.HTTP_POST_CRSF_Mixin) :

        _real_name             = "POST"

    POST = _Changer__POST_ # end class

    @property
    @getattr_safe
    def head_line (self) :
        pass
    # end def head_line

    @property
    @getattr_safe
    def injected_templates (self) :
        return self.parent.form_injected_templates
    # end def injected_templates

    def rendered (self, context, template = None) :
        args     = self.args
        obj      = context ["instance"] = None
        request  = context ["request"]
        response = context ["response"]
        req_data = request.req_data
        parent   = self.parent
        pid      = req_data.get ("pid") or (args [0] if args else None)
        scope    = self.top.scope
        self._check_readonly (request)
        if pid == "null" :
            pid  = None
        if pid is not None :
            obj  = context ["instance"] = self.pid_query_request (pid)
        sid, session_secret = self._new_edit_session (response)
        referrer = "%s%s" % \
            ( request.referrer or parent.abs_href_dynamic
            , parent.href_anchor_pid (obj)
            )
        form = self.form_instance \
            (obj, session_secret = session_secret, sid = sid)
        self.set_request_defaults (form, req_data, scope)
        context.update (form = form, referrer = referrer)
        try :
            self.last_changed = obj.FO.last_changed
        except AttributeError :
            pass
        with self.LET (form = form, referrer = referrer) :
            renderer = response.renderer
            if renderer is not None and renderer.name == "JSON" :
                t      = self.top.Templateer.get_template (form.template_module)
                result = dict \
                    (form = t.call_macro ("main", self, form))
            else :
                result = self.__super.rendered (context, template)
        return result
    # end def rendered

    def set_request_defaults (self, form, req_data, scope) :
        form.set_request_defaults (req_data, scope)
    # end def set_request_defaults

    def _call_submit_callback (self, cb, request, response, scope, fv, result) :
        if TFL.callable (cb) :
            try :
                cb (self, request, response, scope, fv, result)
            except Exception as exc :
                logging.exception \
                    ( "%s._rendered_post:\n    %s\n    -> %s"
                    , self.__class__, request.json ["cargo"], result
                    )
    # end def _call_submit_callback

    def _commit_scope_fv (self, scope, fv, request, response) :
        self.commit_scope (request, response)
    # end def _commit_scope_fv

    def _formatted_submit_elements (self, scope, fv) :
        def _gen (scope, fv) :
            results = {}
            fmt     = "%s:\n    %s"
            for e in fv.elements_transitive () :
                v = e.submitted_value
                if not isinstance (v, dict) :
                    if isinstance (v, MOM.Id_Entity) :
                        v = v.FO
                    yield fmt % (e.id, v)
        return "\n\n".join (_gen (scope, fv))
    # end def _formatted_submit_elements

    def _formatted_submit_entities (self, scope, fv, skip_attrs = {}) :
        result = []
        if fv.essence :
            result = self._formatted_submit_entity_iter (scope, fv, skip_attrs)
        return "\n\n".join (result)
    # end def _formatted_submit_entities

    def _formatted_submit_entity_iter \
            (self, scope, fv, skip_attrs, indent = 4) :
        fmt = "%s :\n%s%s"
        FO  = fv.essence.FO
        for e in fv.elements :
            v = e.submitted_value
            k = e.r_name
            if isinstance (e, MF3.Field_Ref_Hidden) or e.q_name in skip_attrs :
                pass
            elif not TFL.is_undefined (v) :
                value = _T (getattr (FO, k))
                yield fmt % (_T (e.label), " " * indent, value)
            elif isinstance (e, MF3.Field_Rev_Ref) :
                for e_r in e.elements :
                    if e_r.essence :
                        yield "%s %s:\n    %s" % \
                            ( _T (e_r.label), e_r.index
                            , "\n    ".join
                                ( self._formatted_submit_entity_iter
                                    (scope, e_r, skip_attrs, indent + 4)
                                )
                            )
    # end def _formatted_submit_entity_iter

    def _rendered_post (self, request, response) :
        json   = request.json
        scope  = self.top.scope
        Status = self.top.Status
        result = {}
        if json.get ("cancel") :
            ### POST was triggered by the cancel button,
            ### not by the submit button
            scope.rollback ()
        else :
            try :
                cargo = json ["cargo"]
            except KeyError :
                raise self.top.Status.Bad_Request ("Missing cargo")
            try :
                fv = self.form_value (request, cargo)
            except Status.Request_Timeout as exc :
                ### XXX re-authorization form (password only)
                result ["expired"] = "\n".join \
                    ( ( exc.message
                      , _T ("Please reload the page")
                      )
                    )
                return result
            if not fv.submission_errors :
                try :
                    self._commit_scope_fv (scope, fv, request, response)
                except Exception as exc :
                    fv.record_commit_errors (scope, exc)
            result.update (fv.as_json_cargo)
            if fv.errors :
                self._call_submit_callback \
                    ( self.submit_error_callback
                    , request, response, scope, fv, result
                    )
                scope.rollback ()
            else :
                self._call_submit_callback \
                    ( self.submit_callback
                    , request, response, scope, fv, result
                    )
        return result
    # end def _rendered_post

# end class _Changer_

class Add_Rev_Ref (_JSON_Action_) :
    """Add a sub-form for a rev-ref entity."""

    name            = "add_rev_ref"

    def _rendered_post (self, request, response) :
        json         = request.json
        form, field  = self._get_form_field (request, json)
        elem         = field.add ()
        f_ajc        = form.as_json_cargo ### ensure proper ids for "completers"
        t_module     = self.top.Templateer.get_template (elem.template_module)
        html         = t_module.call_macro \
            (elem.template_macro, self, form, elem, t_module)
        result       = dict \
            ( html             = html
            , form_spec_update = elem.as_json_cargo
            )
        return result
    # end def _rendered_post

# end class Add_Rev_Ref

class Instance (_Changer_) :

    argn            = 1
    name            = "change"
    _auth_required  = True

    class _MF3_Delete_ (GTW.RST.DELETE) :

        _real_name             = "DELETE"

        def _response_body (self, resource, request, response) :
            obj = resource.obj
            if obj is None :
                raise resource.Status.Not_Found ()
            else :
                return resource._rendered_delete (request, response, obj)
        # end def _response_body

    DELETE = _MF3_Delete_ # end class

# end class Instance

class Completed (_JSON_Action_PO_) :
    """Return auto completion values for a MF3 page."""

    name                 = "completed"

    def _rendered_post (self, request, response) :
        json         = request.json
        form, field  = self._get_form_field (request, json)
        result       = {}
        scope        = self.top.scope
        completer    = field.completer
        if completer is not None :
            eor    = self.eligible_object_restriction (completer.etn)
            result = completer.choose (scope, json, eor, self.pid_query_request)
        return result
    # end def _rendered_post

# end class Completed

class Completer (_JSON_Action_PO_) :
    """Do auto completion for a MF3 page."""

    name                 = "complete"

    def _rendered_post (self, request, response) :
        json         = request.json
        form, field  = self._get_form_field (request, json)
        result       = dict (matches = [], partial = False)
        scope        = self.top.scope
        completer    = field.completer
        if completer is not None :
            polisher = field.polisher
            if polisher is not None and polisher.pre_complete :
                try :
                    values   = json ["field_values"]
                    pd       = self._polished \
                        (request, response, form, field, json, values)
                    values.update \
                        (zip (pd ["field_ids"], pd ["field_values"]))
                except ValueError :
                    pass
                except Exception as exc :
                    logging.exception (pyk.text_type (exc))
            eor    = self.eligible_object_restriction (completer.etn)
            result = completer.choices (scope, json, eor, self.max_completions)
        return result
    # end def _rendered_post

# end class Completer

class Creator (_Changer_) :
    """Page displaying form for creating a new instance of a etype with an
       MF3 form.
    """

    argn                 = 0
    name                 = "create"

# end class Creator

class Deleter (_JSON_Action_PO_) :
    """Delete a specific instance of a etype."""

    ### `argn = None` because `Deleter` can be `POST`ed to with a `child` or
    ### with a `pid` contained in JSON cargo
    argn                 = None

    name                 = "delete"

    _auth_required       = True

    def _rendered_post (self, request, response) :
        form, field  = self._get_form_field (request, request.json)
        obj          = field.essence
        if obj is not None :
            return self._rendered_delete (request, response, obj)
        else :
            error = _T ("You need to specify a pid!")
            raise self.top.Status.Bad_Request (error)
    # end def _rendered_post

# end class Deleter

class Displayer (GTW.RST.TOP.MOM.Entity_Mixin, GTW.RST.TOP.Page) :

    argn                  = 1
    name                  = "display"
    page_template_name    = "e_type_display"
    static_p              = False

    def __init__ (self, ** kw) :
        ETM = self.parent.ETM
        kw ["obj"] = ETM.pid_query (kw ["args"] [0])
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    @getattr_safe
    def admin (self) :
        return self.parent
    # end def admin

    @Once_Property
    @getattr_safe
    def fields (self) :
        names  = tuple (a.name for a in self.E_Type.edit_attr)
        result = self.admin._fields (names)
        return result
    # end def fields

    @property
    @getattr_safe
    def head_line (self) :
        return self.E_Type.ui_name_T
    # end def head_line

# end class Displayer

class Polisher (_JSON_Action_PO_) :
    """Polish attribute values for a MF3 page."""

    name                 = "polish"

    def _rendered_post (self, request, response) :
        json         = request.json
        form, field  = self._get_form_field (request, json)
        result       = {}
        scope        = self.top.scope
        polisher     = field.polisher
        if polisher is not None :
            try :
                values = json ["field_values"]
            except KeyError :
                raise self.top.Status.Bad_Request ("Missing field values")
            try :
                result = self._polished \
                    (request, response, form, field, json, values)
            except ValueError as exc :
                result ["feedback"] = pyk.text_type (exc)
        else :
            result ["error"] = _T ("Field %s doesn't have a polisher") \
                % (field.label, )
        return result
    # end def _rendered_post

# end class Polisher

class QX_AF_Html (_JSON_Action_PO_) :
    """Process AJAX query for attr-filter's html"""

    name            = "af_html"

    def _rendered_post (self, request, response) :
        result          = {}
        json            = TFL.Record (** request.json)
        E_Type          = self.E_Type
        af              = QR.Filter (E_Type, json.key)
        template        = self.top.Templateer.get_template ("e_type")
        call_macro      = template.call_macro
        result ["html"] = call_macro ("attr_filter_pure", self, af)
        return result
    # end def _rendered_post

# end class QX_AF_Html

class QX_Completed (_JSON_Action_PO_) :
    """Process AJAX query for accepting completion of entity auto completion"""

    name            = "esf_completed"

    def _rendered_post (self, request, response) :
        scope     = self.top.scope
        json      = self._normalized_esf_json (request)
        af        = self._get_esf_filter      (request, json)
        values    = self._get_esf_values      (request, json)
        completer = af.AQ.ESW.completer       (scope, json.trigger_n, values)
        obj       = self.pid_query_request    (json.pid, completer.E_Type_NP)
        instance  = completer.instance        (obj)
        result    = self._rendered_esf \
            ( af
            , callbacks = [] ### XXX
            , ESW       = instance
            , display   = str (obj.FO)
            , value     = obj.pid
            , values    = instance.values
            )
        return result
    # end def _rendered_post

# end class QX_Completed

class QX_Completer (_JSON_Action_PO_) :
    """Process AJAX query for querying completions for entity auto completions"""

    name            = "esf_completer"

    def _rendered_post (self, request, response) :
        scope     = self.top.scope
        json      = self._normalized_esf_json (request)
        af, el    = self._get_attr_filter     (request, json)
        values    = self._get_esf_values      (request, json)
        completer = af.AQ.ESW.completer       (scope, json.trigger_n, values)
        bq        = completer.query ()
        ETM       = completer.ETM
        names     = completer.names
        eor_p     = None if el is None else el.restrict_completion
        if eor_p :
            ### For some attributes, `eligible_object_restriction` is too
            ### restrictive. For instance, an attribute referring to a
            ### person should normally not be restricted even if the user is
            ### only allowed to change his own `PAP.Person` instance
            ###
            ### `eligible_object_restriction` is used in two conflicting
            ### ways:
            ### - to restrict `objects` in `Admin_Restricted`
            ### - to restrict the completions offered in an entity selector
            ###   form: we might want some restrictions here, but not
            ###   necessarily the same ones as for `Admin_Restricted`
            eor   = self.eligible_object_restriction (ETM.type_name)
            if eor is not None :
                bq = bq.filter (eor)
        query     = bq.distinct ()
        entity_p  = getattr (json, "entity_p", False)
        return self._rendered_completions (ETM, query, names, entity_p, json)
    # end def _rendered_post

# end class QX_Completer

class QX_Entity_Selector_Form (_JSON_Action_PO_) :
    """Process AJAX query for entity-selector form"""

    name            = "esf"

    def _rendered_post (self, request, response) :
        return self._rendered_post_esf_form (request, response)
    # end def _rendered_post

# end class QX_Entity_Selector_Form

class QX_Order_By_Form (_JSON_Action_PO_) :
    """Process AJAX query for order-by form"""

    name            = "obf"

    def _rendered_post (self, request, response) :
        HTTP            = self.top.HTTP
        result          = {}
        E_Type          = self.E_Type
        template        = self.top.Templateer.get_template ("e_type")
        call_macro      = template.call_macro
        result ["html"] = call_macro ("order_by_form", self)
        return result
    # end def _rendered_post

# end class QX_Order_By_Form

class QX_Select_Attr_Form (_JSON_Action_PO_) :
    """Process AJAX query for select-attr form"""

    name            = "asf"

    def _rendered_post (self, request, response) :
        HTTP            = self.top.HTTP
        result          = {}
        E_Type          = self.E_Type
        template        = self.top.Templateer.get_template ("e_type")
        call_macro      = template.call_macro
        result ["html"] = call_macro ("select_attr_form", self)
        return result
    # end def _rendered_post

# end class QX_Select_Attr_Form

class Undoer (_JSON_Action_PO_) :
    """Undo a change"""

    argn            = 0
    name            = "undo"
    _auth_required  = True

    def _rendered_post (self, request, response) :
        scope  = self.top.scope
        undo   = TFL.Record (request.json)
        result = {}
        try :
            change = scope.query_changes (cid = undo.cid, pid = undo.pid).one ()
        except Exception as exc :
            error = _T ("You need to specify valid undo information: %s" % exc)
            raise self.top.Status.Bad_Request (error)
        later = scope.query_changes (Q.cid > undo.cid, pid = undo.pid)
        if later :
            result ["error"] = _T \
                ( "Cannot undo a change if %s later changes exist for "
                  "the same object"
                % (later.count ())
                )
        else :
            change.undo (scope)
            obj = scope.pid_query (undo.pid)
            result ["feedback"] = _T \
                ("Successfully revived object %s" % (obj.ui_display, ))
        return result
    # end def _rendered_post

# end class Undoer

class _NC_Mixin_ (TFL.Meta.Object) :

    _v_entry_type_list  = ()

    @classmethod
    @getattr_safe
    def _m_after__init__(cls, name, bases, dct) :
        cls._entry_type_map = etm = {}
        for vet in cls._v_entry_type_list :
            try :
                c = getattr (cls, vet.__name__)
            except AttributeError :
                c = vet
                setattr (cls, vet.__name__, vet)
            etm [c.name] = c
    # end def _m_after__init__

    def _child_kw (self, child, ** kw) :
        result = dict (kw)
        ### GTW.RST.Resource._Base_.__init__ considers
        ###     `child_permission_map` and `child_postconditions_map`
        ### with `kw ["name"]` but the maps refer to just `child`
        if child in self.child_permission_map :
            result ["permission"] = self.child_permission_map [child]
        if child in self.child_postconditions_map :
            result ["postconditions"] = \
                self.child_postconditions_map [child]
        return result
    # end def _child_kw

    def _new_child_x (self, T, child, grandchildren) :
        argn = T.argn
        if argn is None or len (grandchildren) == argn :
            name   = pp_join (* grandchildren) if grandchildren else ""
            kw     = self._child_kw \
                ( child
                , args   = grandchildren
                , kind   = child
                , name   = "%s/%s" % (child, name) if name else child
                , parent = self
                )
            result = T (** kw)
            return result
    # end def _new_child_x

# end class _NC_Mixin_

_Ancestor = GTW.RST.TOP.Dir_V

class _QX_Dispatcher_E_Type_Mixin_ (_NC_Mixin_, _Ancestor) :

    name                  = "qx"

    _v_entry_type_list    = \
        (QX_Completed, QX_Completer, QX_Entity_Selector_Form)

# end class _QX_Dispatcher_E_Type_Mixin_

_Ancestor = _QX_Dispatcher_E_Type_Mixin_

class _QX_Dispatcher_ (_Ancestor) :

    _v_entry_type_list    = _Ancestor._v_entry_type_list + \
        (QX_AF_Html, QX_Order_By_Form, QX_Select_Attr_Form)

# end class _QX_Dispatcher_

_Ancestor = GTW.RST.TOP._Base_

class _Admin_E_Type_Mixin_ (_NC_Mixin_, _Ancestor) :
    """Mixin handling MF3 forms for one E_Type."""

    _real_name                    = "E_Type_Mixin"

    Instance                      = Instance

    max_completions               = 20
    mf3_attr_spec_d               = {}
    nav_off_canvas                = True
    skip_etag                     = True
    submit_callback               = None
    submit_error_callback         = None

    _auth_required                = True
    _exclude_robots               = True
    _greet_entry                  = None
    _list_display                 = None
    _mf3_attr_spec                = {}
    _MF3_Attr_Spec                = {}
    _MF3_Form_Spec                = {}
    _mf3_id_prefix                = "MF3"
    _sort_key                     = None

    _v_entry_type_list            = \
        ( Add_Rev_Ref, Completed, Completer, Creator, Deleter, Displayer
        , Instance, Polisher, Undoer
        , _QX_Dispatcher_E_Type_Mixin_
        )

    @Once_Property
    def et_map_name (self) :
        if not self.implicit :
            return "mf3"
    # end def et_map_name

    @Once_Property
    @getattr_safe
    def Form (self) :
        return MF3.Entity.Auto \
            ( self.E_Type
            , attr_spec = self.MF3_Attr_Spec
            , id_prefix = self.mf3_id_prefix
            , ** self.MF3_Form_Spec
            )
    # end def Form

    @Once_Property
    @getattr_safe
    def form_injected_templates (self) :
        try :
            form = self.Form
        except LookupError :
            renderers = set ()
        else :
            renderers = set (self.Form.template_module_iter ())
        T = self.top.Templateer
        return tuple (T.get_template (r) for r in renderers)
    # end def form_injected_templates

    @property
    @getattr_safe
    def mf3_attr_spec (self) :
        """Attribute specification for MF3 form instance"""
        result = self._mf3_attr_spec
        xtra   = self.mf3_attr_spec_d
        if xtra :
            result = update_combined (result, xtra)
        return result
    # end def mf3_attr_spec

    @mf3_attr_spec.setter
    def mf3_attr_spec (self, value) :
        self._mf3_attr_spec = update_combined (self._mf3_attr_spec, value)
    # end def mf3_attr_spec

    @property
    @getattr_safe
    def MF3_Attr_Spec (self) :
        """Attribute specification for MF3 form class"""
        result = self._MF3_Attr_Spec
        return result
    # end def MF3_Attr_Spec

    @MF3_Attr_Spec.setter
    def MF3_Attr_Spec (self, value) :
        self._MF3_Attr_Spec = update_combined (self._MF3_Attr_Spec, value)
    # end def MF3_Attr_Spec

    @property
    @getattr_safe
    def MF3_Form_Spec (self) :
        """Form specification for MF3 form class"""
        result = self._MF3_Form_Spec
        return result
    # end def MF3_Form_Spec

    @MF3_Form_Spec.setter
    def MF3_Form_Spec (self, value) :
        self._MF3_Form_Spec = update_combined (self._MF3_Form_Spec, value)
    # end def MF3_Form_Spec

    @property
    @getattr_safe
    def mf3_id_prefix (self) :
        return self._mf3_id_prefix
    # end def mf3_id_prefix

    @mf3_id_prefix.setter
    def mf3_id_prefix (self, value) :
        self._mf3_id_prefix = value
    # end def mf3_id_prefix

    @Once_Property
    @getattr_safe
    def qr_spec (self) :
        return QRS (self.E_Type)
    # end def qr_spec

    @property
    @getattr_safe
    def sort_key (self) :
        result = self._sort_key
        if result is None :
            result = self.E_Type.sorted_by_epk
        return result
    # end def sort_key

    @sort_key.setter
    def sort_key (self, value) :
        self._sort_key = value
    # end def sort_key

    def eligible_object_restriction (self, type_name) :
        return None
    # end def eligible_objects

    def href_add_rev_ref (self) :
        return pp_join (self.abs_href_dynamic, "add_rev_ref")
    # end def href_add_rev_ref

    def href_complete (self) :
        return pp_join (self.abs_href_dynamic, "complete")
    # end def href_complete

    def href_completed (self) :
        return pp_join (self.abs_href_dynamic, "completed")
    # end def href_completed

    def href_delete (self, obj = None) :
        result = pp_join (self.abs_href_dynamic, "delete")
        if obj is not None :
            result = pp_join (result, str (obj.pid))
        return result
    # end def href_delete

    def href_instance (self, obj) :
        return pp_join (self.abs_href_dynamic, str (obj.pid))
    # end def href_instance

    def href_polisher (self) :
        return pp_join (self.abs_href_dynamic, "polish")
    # end def href_polisher

    def href_qx_esf_completed (self) :
        return pp_join (self.abs_href_dynamic, self.qx_prefix, "esf_completed")
    # end def href_qx_esf_completed

    def href_qx_esf_completer (self) :
        return pp_join (self.abs_href_dynamic, self.qx_prefix, "esf_completer")
    # end def href_qx_esf_completer

    def href_qx_esf (self) :
        return pp_join (self.abs_href_dynamic, self.qx_prefix, "esf")
    # end def href_qx_esf

    def href_undo (self, change) :
        return pp_join (self.abs_href_dynamic, "undo")
    # end def href_undo

    def is_current_dir (self, page) :
        if not self.hidden :
            p = page.href_dynamic
            s = self.href_dynamic
            return p == s or (p.startswith (s) and p [len (s)] == "/")
    # end def is_current_dir

    def page_from_obj (self, obj) :
        result = self._new_child_x (self.Instance, str (obj.pid), ())
        return result
    # end def page_from_obj

    def template_iter (self) :
        T = self.top.Templateer
        yield self.template
        yield T.get_template \
            (self.Instance.template_name, self.form_injected_templates)
    # end def template_iter

    def _get_child (self, child, * grandchildren) :
        result = self.__super._get_child (child, * grandchildren)
        if result is None and not grandchildren :
            try :
                pid = int (child)
            except ValueError :
                pass
            else :
                result = self.Instance \
                    ( args   = (child, )
                    , kind   = child
                    , name   = child
                    , parent = self
                    , ** self._child_kw ("change")
                    )
        if result is None and self._entry_type_map :
            try :
                T = self._entry_type_map [child]
            except KeyError :
                pass
            else :
                result = self._new_child (T, child, grandchildren)
        return result
    # end def _get_child

    def _new_child (self, T, child, grandchildren) :
        if child == self.qx_prefix and grandchildren :
            new_child = self.__super._new_child
        else :
            new_child = self._new_child_x
        return new_child (T, child, grandchildren)
    # end def _new_child

E_Type_Mixin = _Admin_E_Type_Mixin_ # end class

_Ancestor = GTW.RST.TOP.Dir_V

class E_Type \
        ( GTW.RST.TOP.MOM.Renderer_Mixin
        , _Admin_E_Type_Mixin_
        , GTW.RST.TOP.MOM.E_Type_Mixin
        , _Ancestor
        ) :
    """Directory displaying the instances of one E_Type."""

    css_group             = "Type"
    default_qr_kw         = dict \
        ( limit           = 25
        )
    dir_template_name     = "e_type_admin"
    static_p              = False

    _v_entry_type_list    = _Admin_E_Type_Mixin_._v_entry_type_list [:-1] + \
        ( _QX_Dispatcher_, )

    class _E_Type_GET_ (_Ancestor.GET) :

        _renderers             = \
            _Ancestor.GET._renderers + (GTW.RST.Mime_Type.JSON, )

    GET = _E_Type_GET_ # end class

    class _E_Type_Renderer_ (GTW.RST.TOP.MOM.Renderer.E_Type) :

        _real_name     = "Renderer"
        Action         = GTW.RST.TOP.MOM.Action

        Actions_I      = \
            ( Action.Change
            , Action.Delete
            )

        Actions_T      = \
            ( Action.Create
            ,
            )

        actions_at_top = None

    Renderer = _E_Type_Renderer_ # end class

    def __init__ (self, ** kw) :
        self.pop_to_self (kw, "list_display", prefix = "_")
        self.__super.__init__ (** kw)
    # end def __init__

    @property
    @getattr_safe
    def entries (self) :
        return ()
    # end def entries

    @Once_Property
    def et_map_name (self) :
        if not self.implicit :
            return "admin"
    # end def et_map_name

    @Once_Property
    @getattr_safe
    def fields_default (self) :
        return self._fields  (self.list_display)
    # end def fields_default

    @property
    @getattr_safe
    def head_line (self) :
        co      = getattr (self, "query_size", None)
        if co is None :
            co  = self.count
        qr      = self.query_restriction
        tail    = "%s" % (co, )
        if qr :
            cf  = qr.total_f
            cu  = qr.total_u
            sep = "/"
            if cf and cf != co :
                tail = "%s%s%s" % (tail, sep, cf)
                sep  = "//"
            if cu and cu != cf :
                tail = "%s%s%s" % (tail, sep, cu)
        return "%s (%s)" % (_T (self.ETM.E_Type.ui_name), tail)
    # end def head_line

    @Once_Property
    @getattr_safe
    def list_display (self) :
        result = self._list_display
        if result is None :
            result = self._auto_list_display
        return result
    # end def list_display

    @Once_Property
    @getattr_safe
    def manager (self) :
        return self.etype_manager (self.E_Type)
    # end def manager

    @Once_Property
    @getattr_safe
    def _auto_list_display (self, ) :
        return tuple (a.name for a in self.E_Type.edit_attr)
    # end def _auto_list_display

    def changer (self, pid = None, ** kw) :
        ### Usable by Jinja template to add change button to a html page
        return self.Instance \
            ( parent          = self
            , pid             = pid
            )
    # end def changer

    def href_anchor_pid (self, obj) :
        return "#pk-%s" % (obj.pid, ) if obj else ""
    # end def href_anchor_pid

    def href_create (self) :
        return pp_join (self.abs_href_dynamic, "create")
    # end def href_create

    def href_change (self, obj) :
        return pp_join (self.abs_href_dynamic, "change", str (obj.pid))
    # end def href_change

    def href_display (self, obj = None) :
        man = self.manager
        if man :
            return man.href_display (obj)
        elif obj is not None :
            return pp_join (self.abs_href_dynamic, "display", str (obj.pid))
    # end def href_display

    def href_qx_af_html (self) :
        return pp_join (self.abs_href_dynamic, self.qx_prefix, "af_html")
    # end def href_qx_af_html

    def href_qx_asf (self) :
        return pp_join (self.abs_href_dynamic, self.qx_prefix, "asf")
    # end def href_qx_asf

    def href_qx_obf (self) :
        return pp_join (self.abs_href_dynamic, self.qx_prefix, "obf")
    # end def href_qx_obf

    def rendered (self, context, template = None) :
        objects  = self.objects
        qr       = self.query_restriction
        request  = context ["request"]
        response = context ["response"]
        with self.LET (query_size = len (objects)) :
            context.update \
                ( fields            = self.fields
                , objects           = objects
                , query_restriction = qr
                , query_size        = self.query_size
                )
            renderer = self.renderer
            if response.renderer and response.renderer.name == "JSON" :
                template   = self.top.Templateer.get_template \
                    (renderer.template_module)
                call_macro = template.call_macro
                result     = dict \
                    ( callbacks        = ["setup_obj_list"]
                    , head_line        = self.head_line
                    , limit            = qr.limit
                    , object_container = call_macro
                        ("E_Type", renderer, t_class = "Object-List")
                    , offset           = qr.offset
                    , qr_next_p        = qr.next_p
                    , qr_prev_p        = qr.prev_p
                    )
            else :
                result = self.__super.rendered (context, template)
        return result
    # end def rendered

    def _fix_filters (self, filters) :
        scope = self.top.scope
        for f in filters :
            if isinstance (f.AQ, MOM.Attr.Querier.Id_Entity) and f.value :
                try :
                    o = scope.pid_query (int (f.value))
                except (TypeError, ValueError, LookupError) :
                    pass
                else :
                    f.ui_display = o.ui_display
    # end def _fix_filters

    @TFL.Contextmanager
    def _handle_method_context (self, method, request, response) :
        qr = QR.from_request \
            ( self.top.scope, self.E_Type, request
            , ** self.default_qr_kw
            )
        self._fix_filters (qr.filters)
        with self.LET (query_restriction = qr) :
            with self.__super._handle_method_context \
                    (method, request, response) :
                yield
    # end def _handle_method_context

    def _renderer_fields (self) :
        qr_attrs = self.query_restriction.attributes
        return self._fields (qr_attrs) if qr_attrs else self.fields_default
    # end def _renderer_fields

# end class E_Type

class E_Type_Alias (GTW.RST.TOP.Alias) :

    ETM                   = property \
        ( lambda s        : s.target.ETM
        , lambda s, v     : None
        )

    short_title           = property \
        ( lambda s        : s.target.ETM.ui_name_T
        , lambda s, v     : None
        )

    title                 = property \
        ( lambda s        : s.target.title
        , lambda s, v     : None
        )
    static_p              = False

    _exclude_robots       = True

# end class E_Type_Alias

_Ancestor = GTW.RST.TOP.Dir

class Group (_Ancestor) :
    """Directory displaying a group of E_Type admin pages."""

    _etypes               = []
    _PNSs                 = []

    css_group             = "Group"
    dir_template_name     = "site_admin"
    show_aliases          = False
    static_p              = False

    _exclude_robots       = True
    _auth_required        = True


    def __init__ (self, ** kw) :
        self.pop_to_self (kw, "etypes", "PNSs", prefix = "_")
        self.__super.__init__ (** kw)
    # end def __init__

    @property
    @getattr_safe
    def entries (self) :
        if not self._entries :
            entries = self._filter_etype_entries \
                (self._etypes, self._pns_entries (* self._PNSs))
            self.add_entries (* entries)
        return self._entries
    # end def entries

    def template_iter (self) :
        for t in self.__super.template_iter () :
            yield t
        for e in self.entries :
            for t in e.template_iter () :
                yield t
    # end def template_iter

    def _add_index (self, l) :
        self._entries.sort (key = TFL.Getter.short_title)
        self.__super._add_index (0)
    # end def _add_index

    def _etype_entry (self, ET) :
        ET_Map = self.top.ET_Map
        tn     = ET.type_name
        admin  = ET_Map [tn].admin
        if (not admin) or self.show_aliases :
            aa = dict (getattr (ET, "admin_args", {}))
            aa.update (ET.UI_Spec, ETM = tn)
            T = E_Type
            if admin :
                T = E_Type_Alias
                aa.update \
                    ( name          = ET.ui_name
                    , show_in_admin = True
                    , target        = admin
                    )
            if aa.get ("show_in_admin") :
                return T (parent = self, ** aa)
    # end def _etype_entry

    def _filter_etype_entries (self, * args) :
        seen = set ()
        for e in iter_chain (* args) :
            if isinstance (e, pyk.string_types) :
                e = self._etype_entry (self.top.scope [e].E_Type)
                if e is None :
                    continue
            elif isinstance (e, tuple) :
                cls, args, kw = e
                e = cls (* args, ** dict (kw, parent = self))
            etn = e.type_name
            if etn not in seen :
                seen.add (etn)
                yield e
    # end def _filter_etype_entries

    def _pns_entries (self, * pnss) :
        app_type = self.top.App_Type
        ET_Map   = self.top.ET_Map
        seen     = set ()
        for pns in pnss :
            PNS = app_type.PNS_Map [pns]
            for ET in app_type.etypes_by_pns [pns] :
                if ET.is_relevant and ET.show_in_ui :
                    tbn = ET.type_base_name
                    if tbn not in seen :
                        e = self._etype_entry (ET)
                        if e is not None :
                            seen.add (tbn)
                            yield e
    # end def _pns_entries

# end class Group

class Site (Group) :
    """Directory displaying admin Groups."""

    pid                  = "Admin"
    static_p              = False

    _exclude_robots      = True
    _auth_required       = True

    def _auto_entries (self) :
        for et in pyk.itervalues (self.top.ET_Map) :
            man = et.manager
            if man is not None and et.admin is None :
                m_kw        = man.admin_args.copy ()
                short_title = m_kw.pop ("short_title", man.short_title)
                title       = m_kw.pop \
                    ("title", "%s: %s" % (self.title, man.name))
                ETM         = m_kw.pop ("ETM", man._ETM)
                Type        = m_kw.pop ("Type", E_Type)
                e           = Type \
                    ( ETM         = ETM
                    , name        = man.name
                    , parent      = self
                    , short_title = short_title
                    , title       = title
                    , ** m_kw
                    )
                yield e
    # end def _auto_entries

    def _filter_etype_entries (self, * args) :
        return self.__super._filter_etype_entries \
            (self._auto_entries (), * args)
    # end def _filter_etype_entries

# end class Site

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Admin
