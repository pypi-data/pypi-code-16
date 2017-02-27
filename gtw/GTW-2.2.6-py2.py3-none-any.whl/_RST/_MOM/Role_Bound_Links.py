# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.MOM.Role_Bound_Links
#
# Purpose
#    Provide RESTful resource for role-bound links of a specific instance
#
# Revision Dates
#    17-May-2013 (CT) Creation
#     3-Jun-2013 (CT) Use `.attr_prop` to access attribute descriptors
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST.HTTP_Method
import _GTW._RST._MOM.Mixin
import _GTW._RST._MOM.E_Type

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe

import _TFL._Meta.Object

from   posixpath                import join as pp_join

_Ancestor = GTW.RST.Leaf

class _RST_MOM_Role_Bound_Links_ (GTW.RST.MOM.E_Type_Mixin, _Ancestor) :
    """RESTful resource for role-bound links of a specific instance"""

    _real_name                 = "Role_Bound_Links"

    class _RST_MOM_Role_Bound_Links_GET_ (GTW.RST.MOM.E_Type.GET) :

        _real_name             = "GET"

        def _response_body_count (self, resource, request, response) :
            return resource.query ().count ()
        # end def _response_body_count

    GET = _RST_MOM_Role_Bound_Links_GET_ # end class

    class _RST_MOM_Role_Bound_Links_POST_ (GTW.RST.MOM.E_Type.POST) :

        _real_name                 = "POST"

        def _apply_attrs (self, resource, request, response, attrs) :
            lra = resource.link_ref_attr
            obj = resource.obj
            for name in lra.name, lra.role_name :
                if name in attrs and attrs [name] != obj :
                    raise ValueError \
                        ("Cannot set %s value to %s" % (name, attrs [name]))
            attrs [lra.ref_name] = resource.role
            return self.__super._apply_attrs \
                (resource, request, response, attrs)
        # end def _apply_attrs

        def _obj_resource_response_body \
                (self, obj, resource, request, response) :
            o_resource, o_body = self.__super._obj_resource_response_body \
                (obj, resource.ref_resource, request, response)
            return o_resource, o_body
        # end def _obj_resource_response_body

    POST = _RST_MOM_Role_Bound_Links_POST_ # end class

    def __init__ (self, name, ** kw) :
        self.role          = role = self.parent.obj
        self.link_ref_attr = lra  = role.attr_prop (name)
        self._ETM          = lra.E_Type.type_name
        self.__super.__init__ (name = name, ** kw)
    # end def __init__

    @Once_Property
    @getattr_safe
    def query_filters (self) :
        return (self.link_ref_attr.ref_filter == self.role, )
    # end def query_filters

    @Once_Property
    @getattr_safe
    def ref_resource (self) :
        return self.resource_from_e_type (self.type_name)
    # end def ref_resource

    def href_obj (self, obj) :
        return pp_join (self.ref_resource.abs_href_dynamic, str (obj.pid))
    # end def href_obj

    def query (self, sort_key = None) :
        result = self.link_ref_attr.query_x \
            (self.role, sort_key = sort_key or self.sort_key)
        return result
    # end def query

    def _new_entry (self, instance, ** kw) :
        resource = self.ref_resource
        return resource.Entity (obj = instance, parent = resource, ** kw)
    # end def _new_entry

Role_Bound_Links = _RST_MOM_Role_Bound_Links_ # end class

if __name__ != "__main__" :
    GTW.RST.MOM._Export ("*")
### __END__ GTW.RST.MOM.Role_Bound_Links
