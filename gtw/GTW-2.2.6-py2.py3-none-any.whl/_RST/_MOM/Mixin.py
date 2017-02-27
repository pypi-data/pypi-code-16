# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.MOM.Mixin
#
# Purpose
#    Define mixin classes for GTW.RST.MOM
#
# Revision Dates
#    22-Jun-2012 (CT) Creation
#     3-Jul-2012 (CT) Factored from _GTW/_RST/MOM.py
#     3-Jul-2012 (CT) Add support for `Query_Restriction`
#     5-Jul-2012 (CT) Add support for nested entities to `_PUT_POST_Mixin_`
#                     * factor `_resolve_request_attrs`
#                     * add and use `_resolve_nested_request_attrs`
#    17-Jul-2012 (CT) Factor `_changed_cid`
#    17-Jul-2012 (CT) Include `_change_info` in `_handle_method_context`
#    18-Jul-2012 (CT) Use `scope.pid_query`, not `ETM.pid_query`, in
#                     `_get_child_query` (don't want `Gone` for type mismatch)
#    19-Jul-2012 (CT) Add `RST_Entity_Mixin`: factored from `GTW.RST.MOM.Entity`
#    19-Jul-2012 (CT) Change `RST_E_Type_Mixin._get_child` to call
#                     `__super._get_child` before, not after, `_get_child_query`
#    19-Jul-2012 (CT) Turn `_change_info` into property, use `top._change_infos`
#    20-Jul-2012 (CT) Factor `pid_query_request`
#    23-Jul-2012 (CT) Add argument `response` to `_handle_method_context`
#    31-Jul-2012 (CT) Use `formatted_1`, not `repr`, in `_resolve_request_attrs`
#     2-Aug-2012 (CT) Use `id_entity_attr` in
#                     `RST_Entity_Mixin.change_query_filters`
#     5-Aug-2012 (CT) Change `pid_query_request` to handle `result is None`
#     6-Aug-2012 (CT) Change `etag` in `_get_change_info`
#     7-Aug-2012 (CT) Factor `RST_Base_Mixin`
#     7-Aug-2012 (CT) Change class prefix from `RST_` to `_RST_MOM_`,
#                     add class suffix `_`, add `_real_name`
#     5-Oct-2012 (CT) Change `attributes.setter` to pass `Kind` instances
#     5-Oct-2012 (CT) Add `attributes.deleter`
#    10-Oct-2012 (CT) Pass `error` to `Status.Gone`
#    17-Oct-2012 (CT) Change `_PUT_POST_Mixin_` to use `raw`
#     9-Nov-2012 (CT) Factor `_get_child_page`
#    21-Nov-2012 (CT) Fix `attributes.setter` for composite attributes
#    21-Nov-2012 (CT) Add exception handler to
#                     `E_Type_Mixin._handle_method_context`
#    27-Nov-2012 (CT) Factor `_obj_resource_response_body`, add `_POST_Mixin_`
#     7-Dec-2012 (CT) Add `E_Type_Mixin.dont_et_map`
#     7-Dec-2012 (CT) Split `query_filters` into `query_filters_d` and
#                     `query_filters_s`
#     7-Dec-2012 (CT) Factor `_change_info_key`
#    11-Dec-2012 (CT) Factor `_check_pid_gone`, pass change-info to `Gone`
#    11-Dec-2012 (CT) Lift `query_filters` from `E_Type_Mixin` to `Mixin`
#    17-Dec-2012 (CT) Add and use `E_Type_Mixin.et_map_name`
#    17-Dec-2012 (CT) Make property `objects` `getattr_safe`
#     2-Mar-2013 (CT) Use `response.headers.set`, not dict assignment
#     2-Mar-2013 (CT) Add `add_doc_link_header`
#    28-Mar-2013 (CT) Change `attributes` to use default `E_Type.ui_attr`
#     9-Apr-2013 (CT) Catch `ValueError` in `_handle_method_context`
#    25-Apr-2013 (CT) Add `Pre_Commit_Entity_Check`, use `resource.commit_scope`
#    30-Apr-2013 (CT) Add `Pre_Commit_Entity_Check.__repr__`
#     1-May-2013 (CT) Improve error message of `_handle_method_context`
#    17-May-2013 (CT) Add `request._rst_seen`  (in `_handle_method_context`)
#    29-Jul-2013 (CT) Accept GET-output in `_resolve_nested_request_attrs`
#     4-Oct-2013 (CT) Factor `Base_Mixin._gen_attr_kinds`
#     4-Oct-2013 (CT) Add `add_fields` to `E_Type_Mixin._handle_method_context`
#     4-Oct-2013 (CT) Fix `E_Type_Mixin._handle_method_context` (use tuple)
#    28-Mar-2014 (CT) Add `Base_Mixin.q_able_attributes`
#    29-Apr-2014 (CT) Make `_old_cid` dependent on `_change_info_key`
#    13-Sep-2014 (CT) Factor `change_query_types`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST.HTTP_Method
import _GTW._RST._MOM.Query_Restriction

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.portable_repr       import portable_repr
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object
import _TFL.Record

class Pre_Commit_Entity_Check (TFL.Meta.Object) :

    def __init__ (self, check_name) :
        self.check_name = check_name
    # end def __init__

    def __call__ (self, resource, request, response) :
        scope = resource.scope
        cname = self.check_name
        for e, acs in scope.uncommitted_changes.entity_changes (scope) :
            check = getattr (e, cname, None)
            if check is not None :
                check (resource, request, response, acs)
    # end def __call__

    def __repr__ (self) :
        return "<%s for %s>" % (self.__class__.__name__, self.check_name)
    # end def __repr__

# end class Pre_Commit_Entity_Check

class _PUT_POST_Mixin_ (GTW.RST.HTTP_Method) :

    failure_code = 400 ### Bad request

    def _obj_resource_response_body (self, obj, resource, request, response) :
        o_resource = resource._new_entry (obj)
        o_body     = o_resource.GET ()._response_body \
            (o_resource, request, response)
        return o_resource, o_body
    # end def _obj_resource_response_body

    def _request_attrs (self, resource, request, response) :
        if request.ckd :
            raise ValueError \
                ("%s doesn't allow cooked values" % (self.name, ))
        try :
            result = request.json ["attributes_raw"]
        except KeyError :
            raise ValueError \
                ("""You need to send the attributes defining """
                 """the object with the request in `attributes_raw`"""
                 """(content-type "application/json")"""
                )
        else :
            self._resolve_request_attrs \
                (resource, request, response, resource.E_Type, result)
        return result
    # end def _request_attrs

    def _resolve_nested_request_attrs \
            (self, resource, request, response, E_Type, attrs) :
        ieas  = E_Type.id_entity_attr
        scope = resource.scope
        for iea in ieas :
            k = iea.name
            if k in attrs :
                etn = iea.E_Type.type_name
                ETM = scope [etn]
                v   = attrs [k]
                if isinstance (v, dict) and set (v) == set (("pid", "url")) :
                    ### pid/url json object as produced by `GET`
                    v = v ["pid"]
                if isinstance (v, dict) :         ### attribute dictionary
                    self._resolve_request_attrs \
                        (resource, request, response, iea.E_Type, v)
                    v = ETM.instance_or_new (raw = True, ** v)
                elif isinstance (v, int) :        ### pid
                    v = scope.pid_query (v)
                elif isinstance (v, pyk.string_types) : ### single epk argument
                    v = ETM.instance_or_new (v, raw = True)
                elif isinstance (v, list) :       ### list of epk arguments
                    v = ETM.instance_or_new (* v, raw = True)
                else :
                    raise ValueError \
                        ("Invalid value %r for %s" % (v, etn))
                attrs [k] = v
    # end def _resolve_nested_request_attrs

    def _resolve_request_attrs \
            (self, resource, request, response, E_Type, attrs) :
        allowed  = set   (a.name for a in E_Type.edit_attr)
        invalids = tuple (k for k in attrs if k not in allowed)
        if invalids :
            raise ValueError \
                ( "Request contains invalid attribute names "
                + portable_repr (invalids)
                )
        self._resolve_nested_request_attrs \
            (resource, request, response, E_Type, attrs)
    # end def _resolve_request_attrs

    def _response_body (self, resource, request, response) :
        try :
            attrs = self._request_attrs (resource, request, response)
            obj   = self._apply_attrs   (resource, request, response, attrs)
            resource.commit_scope       (request, response)
        except Exception as exc :
            result               = dict (error = str (exc))
            response.status_code = self.failure_code
            resource.scope.rollback ()
        else :
            response.status_code = self.success_code
            _, result = self._obj_resource_response_body \
                (obj, resource, request, response)
        return result
    # end def _response_body

# end class _PUT_POST_Mixin_

class _POST_Mixin_ (_PUT_POST_Mixin_) :

    def _obj_resource_response_body (self, obj, resource, request, response) :
        o_resource, o_body = self.__super._obj_resource_response_body \
            (obj, resource, request, response)
        response.set_header ("Location", o_resource.abs_href)
        return o_resource, o_body
    # end def _obj_resource_response_body

# end class _POST_Mixin_

class _RST_MOM_Base_Mixin_ (TFL.Meta.Object) :
    """Base mixin for MOM-specific RST classes."""

    _real_name                 = "Base_Mixin"
    _attributes                = None

    @Once_Property
    @getattr_safe
    def E_Type (self) :
        ETM = self._ETM
        if isinstance (ETM, pyk.string_types) :
            result = self.top.App_Type [ETM]
        else :
            result = ETM.E_Type
        return result
    # end def E_Type

    @property
    @getattr_safe
    def attributes (self) :
        result = self._attributes
        if result is None :
            result = self._attributes = self.E_Type.edit_attr
        return result
    # end def attributes

    @attributes.setter
    def attributes (self, value) :
        self._attributes = \
            tuple (self._gen_attr_kinds (value)) if value is not None else None
    # end def attributes

    @attributes.deleter
    def attributes (self) :
        self._attributes = None
    # end def attributes

    @Once_Property
    @getattr_safe
    def q_able_attributes (self) :
        result = tuple \
            ( a for a in MOM.Attr.Selector.ui_attr (self.E_Type)
              if a.electric
            )
        return result
    # end def q_able_attributes

    @Once_Property
    @getattr_safe
    def type_name (self) :
        return self.E_Type.type_name
    # end def type_name

    def _gen_attr_kinds (self, vs) :
        ET = self.E_Type
        AQ = ET.AQ
        for v in vs :
            if isinstance (v, pyk.string_types) :
                try :
                    v = getattr (AQ, v)._attr
                except AttributeError as exc :
                    print ("*" * 4, exc, ET, v)
                    pass
                else :
                    yield v.kind
            elif isinstance (v, MOM.Attr.Kind) :
                yield v
    # end def _gen_attr_kinds

Base_Mixin = _RST_MOM_Base_Mixin_ # end class

class _RST_MOM_Mixin_ (Base_Mixin) :
    """Mixin for MOM-specific RST classes dealing with entities living in a scope."""

    _real_name                 = "Mixin"

    _exclude_robots            = True
    _objects                   = []
    _sort_key_cid_reverse      = TFL.Sorted_By ("-cid")

    show_rels                  = None

    @Once_Property
    @getattr_safe
    def ETM (self) :
        result = self._ETM
        if isinstance (result, pyk.string_types) :
            result = self.top.scope [result]
        return result
    # end def ETM

    @property
    @getattr_safe
    def change_info (self) :
        result = self._change_info
        if result is None :
            result = self._change_info = self._get_change_info ()
        return result
    # end def change_info

    @property
    @getattr_safe
    def objects (self) :
        return self._get_objects ()
    # end def objects

    @property
    @getattr_safe
    def query_filters (self) :
        return self.query_filters_d + self.query_filters_s
    # end def query_filters

    @property
    @getattr_safe
    def query_filters_d (self) :
        """Dynamic query filters"""
        return tuple ()
    # end def query_filters_d

    @Once_Property
    @getattr_safe
    def query_filters_s (self) :
        """Static query filters: evaluated only once and cached"""
        return tuple ()
    # end def query_filters_s

    @property
    @getattr_safe
    def _change_info (self) :
        return self.top._change_infos.get (self._change_info_key)
    # end def _change_info

    @_change_info.setter
    def _change_info (self, value) :
        self.top._change_infos [self._change_info_key] = value
    # end def _change_info

    @property
    @getattr_safe
    def _change_info_key (self) :
        return self.href
    # end def _change_info_key

    @property
    @getattr_safe
    def _old_cid (self) :
        return self.top._old_cids.get (self._change_info_key, -1)
    # end def _old_cid

    @_old_cid.setter
    def _old_cid (self, value) :
        self.top._old_cids [self._change_info_key] = value
    # end def _old_cid

    def add_doc_link_header (self, response) :
        top = self.top
        etd = top.ET_Map.get (self.type_name)
        if etd :
            doc = getattr (etd, "doc", None) or getattr (etd, "rest_doc", None)
            if doc is not None :
                response.add_link ("doc", doc.abs_href)
    # end def add_doc_link_header

    def pid_query_request (self, pid, E_Type = None, raise_not_found = True) :
        if E_Type is None :
            E_Type = self.E_Type
        scope  = self.top.scope
        Status = self.Status
        try :
            ipid = int (pid)
        except (ValueError, TypeError) :
            pass
        else :
            try :
                result = scope.pid_query (ipid)
            except LookupError as exc :
                self._check_pid_gone (ipid, E_Type, scope)
            else :
                if result is None :
                    self._check_pid_gone (ipid, E_Type, scope)
                elif isinstance (result, E_Type) :
                    return result
                elif raise_not_found :
                    error = \
                        (  _T ("`%s` refers to %s, not %s")
                        % (pid, _T (result.E_Type.ui_name), _T (E_Type.ui_name))
                        )
                    raise Status.Bad_Request (error)
        if raise_not_found :
            error = (_T ("%s `%s` doesn't exist!") % (_T (E_Type.ui_name), pid))
            raise Status.Not_Found (error)
    # end def pid_query_request

    def query_changes (self) :
        scope = self.top.scope
        cqfs  = self.change_query_filters
        if cqfs is not None :
            return scope.query_changes \
                (* cqfs).order_by (self._sort_key_cid_reverse)
    # end def query_changes

    def _changed_cid (self) :
        change_info = self.change_info
        cid         = change_info.cid if change_info else None
        if self._old_cid != cid :
            return cid
    # end def _changed_cid

    def _change_query_types (self, E_Type) :
        if E_Type.is_partial :
            result = set (E_Type.children_np)
        else :
            result = set (E_Type.children)
            result.add   (E_Type.type_name)
        return result
    # end def _change_query_types

    def _check_pid_gone (self, pid, E_Type, scope) :
        lc = scope.query_changes \
            (pid = pid).order_by (self._sort_key_cid_reverse).first ()
        if lc is not None :
            user = _T ("anonymous")
            if lc.user :
                try :
                    user = scope.pid_query (lc.user)
                except Exception :
                    user = lc.user
                else :
                    if user.person :
                        user = user.person
                    user = pyk.text_type (user.FO)
            error = \
                (  _T ("%s `%s` doesn't exist anymore!")
                % (_T (E_Type.ui_name), pid)
                )
            info  = \
                ( _T ("It was deleted by user `%s` on %s")
                % (user, lc.time.strftime ("%Y-%m-%d %H:%M"))
                )
            raise self.Status.Gone (error, info = info)
    # end def _check_pid_gone

    def _get_change_info (self) :
        result = None
        qc     = self.query_changes ()
        if qc is not None :
            lc = qc.first ()
            if lc is not None :
                lm = lc.time.replace (microsecond = 0)
                result  = TFL.Record \
                    ( cid           = lc.cid
                    , etag          = str (lc.cid)
                    , last_modified = lm
                    )
        return result
    # end def _get_change_info

    def _get_objects (self) :
        cid = self._changed_cid ()
        if cid is not None :
            self._objects = self.query ().all ()
            self._old_cid = cid
        return self._objects
    # end def _get_objects

    @TFL.Contextmanager
    def _handle_method_context (self, method, request, response) :
        with self.__super._handle_method_context (method, request, response) :
            with self.LET (_change_info = self._get_change_info ()) :
                with request.LET (_rst_seen = set ()) :
                    yield
    # end def _prepare_handle_method

Mixin = _RST_MOM_Mixin_ # end class

class _RST_MOM_Entity_Mixin_ (Mixin) :
    """Mixin for classes of handling E_Type instances."""

    _real_name                 = "Entity_Mixin"

    @Once_Property
    @getattr_safe
    def change_query_filters (self) :
        result = ()
        obj    = self.obj
        if obj :
            result = (Q.pid == obj.pid, )
            E_Type = obj.__class__
            if E_Type.id_entity_attr :
                def _gen (self, E_Type) :
                    yield obj.pid
                    for iea in E_Type.id_entity_attr :
                        v = iea.get_value (obj)
                        if v and v.pid :
                            yield v.pid
                pids = tuple (_gen (self, E_Type))
                if len (pids) > 1 :
                    result = (Q.pid.IN (pids), )
        return result
    # end def change_query_filters

Entity_Mixin = _RST_MOM_Entity_Mixin_ # end class

class _RST_MOM_E_Type_Mixin_ (Mixin) :
    """Mixin for classes of handling E_Types."""

    _real_name                 = "E_Type_Mixin"

    QR                         = GTW.RST.MOM.Query_Restriction

    default_qr_kw              = dict ()
    dont_et_map                = False
    et_map_name                = None
    query_restriction          = None
    sort_key                   = None

    def __init__ (self, ** kw) :
        self.pop_to_self (kw, "ETM", prefix = "_")
        if "name" not in kw :
            kw ["name"] = self.type_name.replace (".", "-")
        self.__super.__init__ (** kw)
        if self.et_map_name and not self.dont_et_map :
            setattr (self.top.ET_Map [self.type_name], self.et_map_name, self)
    # end def __init__

    @property
    @getattr_safe
    def count (self) :
        if self.query_filters :
            result = self.query ().count ()
        else :
            result = self.ETM.count
        return result
    # end def count

    @Once_Property
    @getattr_safe
    def change_query_filters (self) :
        E_Type = self.E_Type
        if E_Type.type_name == "MOM.Id_Entity" :
            result = ()
        else :
            cqts = self.change_query_types
            if E_Type.is_partial or len (cqts) > 1 :
                result = (Q.type_name.IN (sorted (cqts)), )
            else :
                result = (Q.type_name == E_Type.type_name, )
        return result
    # end def change_query_filters

    @Once_Property
    @getattr_safe
    def change_query_types (self) :
        return self._change_query_types (self.E_Type)
    # end def change_query_types

    def query (self, sort_key = None) :
        result = self.ETM.query \
            (* self.query_filters, sort_key = sort_key or self.sort_key)
        if self.query_restriction is not None :
            result = self.query_restriction (result)
        return result
    # end def query

    def _get_child (self, child, * grandchildren) :
        self.objects ### trigger recomputation/load-from-db, if necessary
        result = self.__super._get_child (child, * grandchildren)
        if result is None :
            obj = self._get_child_query (child)
            if obj is not None :
                result = self._get_child_page (obj)
                if grandchildren :
                    result = result._get_child (* grandchildren)
                return result
        return result
    # end def _get_child

    def _get_child_page (self, obj) :
        return self._new_entry (obj)
    # end def _get_child_page

    def _get_child_query (self, child) :
        return self.pid_query_request (child, raise_not_found = False)
    # end def _get_child_query

    def _get_objects (self) :
        _old_objects = self._objects
        result       = self.__super._get_objects ()
        if result is not _old_objects :
            ### invalidate `_entry_map`, `_entries`
            self._entry_map = {}
            self._entries   = []
        return result
    # end def _get_objects

    @TFL.Contextmanager
    def _handle_method_context (self, method, request, response) :
        with self.__super._handle_method_context (method, request, response) :
            try :
                qr = self.QR.from_request \
                    (self.scope, self.E_Type, request, ** self.default_qr_kw)
            except (AttributeError, TypeError, ValueError) as exc :
                error = _T ("Query restriction triggered error: %s '%s'") % \
                    (exc.__class__.__name__, exc)
                raise self.Status.Bad_Request (error)
            kw = dict (query_restriction = qr)
            if qr.attributes :
                kw ["attributes"] = qr.attributes
            if qr :
                ### temporarily invalidate cached information to trigger
                ### reload with `query_restriction`
                ### old caches will be restored after `_handle_method` completes
                kw.update \
                    ( _change_info = None
                    , _entries     = []
                    , _entry_map   = {}
                    , _objects     = []
                    , _old_cid     = object ()
                    )
            if "add_fields" in request.req_data :
                kw ["add_attributes"] = tuple \
                    ( self._gen_attr_kinds
                        (request.req_data ["add_fields"].split (","))
                    )
            with self.LET (** kw) :
                yield
    # end def _handle_method_context

    def _new_entry (self, instance, ** kw) :
        return self.Entity (obj = instance, parent = self, ** kw)
    # end def _new_entry

E_Type_Mixin = _RST_MOM_E_Type_Mixin_ # end class

if __name__ != "__main__" :
    GTW.RST.MOM._Export ("*", "_PUT_POST_Mixin_", "_POST_Mixin_")
### __END__ GTW.RST.MOM.Mixin
