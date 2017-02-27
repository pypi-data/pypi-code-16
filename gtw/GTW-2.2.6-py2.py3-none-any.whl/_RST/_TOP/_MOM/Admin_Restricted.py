# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.MOM.Admin_Restricted
#
# Purpose
#    Directories and pages for restricted managing instances of MOM E-types
#
# Revision Dates
#    14-Dec-2012 (CT) Creation
#     5-Feb-2015 (CT) Remove `vip_button_p`
#    17-Mar-2015 (CT) Define `_objects` property to use user-specific cache
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from    _GTW._RST._TOP._MOM.Admin import *
from   _TFL.I18N                  import _, _T, _Tn

Admin = GTW.RST.TOP.MOM.Admin

class E_Type_R (Admin.E_Type) :
    """Directory displaying the restricted instances of one E_Type."""

    _real_name            = "E_Type"

    et_map_name           = None
    skip_etag             = True
    restriction_desc      = _ ("created by")

    @property
    @getattr_safe
    def head_line (self) :
        result = self.__super.head_line
        user   = self.user_restriction
        if user :
            u = user.FO
            result = "%s: %s %s" % (result, _T (self.restriction_desc), u)
        return result
    # end def head_line

    @property
    @getattr_safe
    def query_filters_d (self) :
        result = self.query_filters_restricted ()
        if result is None :
            result = (Q.pid == 0) ### don't show any entries
        return (result, ) + self.__super.query_filters_d
    # end def query_filters_d

    @property
    @getattr_safe
    def user_restriction (self) :
        return self.top.user
    # end def user_restriction

    @property
    @getattr_safe
    def _change_info_key (self) :
        user = self.top.user
        pid  = user.pid if user else None
        return self.__super._change_info_key, pid
    # end def _change_info_key

    def query_filters_restricted (self) :
        """Query filter restricting the entities available to resource"""
        user = self.user_restriction
        if user is not None :
            return Q.created_by == user
    # end def query_filters_restricted

    @property
    @getattr_safe
    def _objects (self) :
        return self.top._objects_cache.get (self._change_info_key)
    # end def _objects

    @_objects.setter
    def _objects (self, value) :
        self.top._objects_cache [self._change_info_key] = value
    # end def _objects

E_Type = E_Type_R # end class

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Admin_Restricted
