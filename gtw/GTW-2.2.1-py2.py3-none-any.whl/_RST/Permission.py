# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.RST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.RST.Permission
#
# Purpose
#    Classes modelling permissions for accessing RESTful resources
#
# Revision Dates
#    16-Jan-2010 (CT) Creation
#    18-Jan-2010 (CT) `In_Page_Group` removed
#    26-Feb-2010 (CT) `Is_Superuser` added
#     8-Jun-2012 (CT) Add `Login_Required`, add guards for `user`
#    11-Jun-2012 (CT) Add `rank`
#    20-Jun-2012 (CT) Remove dependency on `GTW.NAV.Root.top`
#     5-Jul-2012 (CT) Move from `GTW.NAV` to `GTW.RST`
#    10-Aug-2012 (CT) Rename `rank` to `_rank`
#    14-Dec-2012 (CT) Remove `Login_Required`
#                     (use `login_required` argument to GTW.Resource instead)
#    14-Dec-2012 (CT) Adapt `Is_Creator` to changes of `MOM.Entity`
#    20-Jan-2015 (CT) Factor `_get_obj`, consider `kw ["obj"]`
#    21-Jan-2015 (CT) Factor `_User_Matches_Attribute_`
#    21-Jan-2015 (CT) Add `Login_has_Person`
#    21-Jan-2015 (CT) Add `_Permission_.instance`, `_M_Permission_.instance`
#     5-Feb-2015 (CT) Add `_User_Person_Matches_Attribute_`
#    21-Sep-2015 (CT) Add `auth_required`, `message`
#    ««revision-date»»···
#--

from   _TFL                     import TFL
from   _GTW                     import GTW

import _GTW._RST

from   _TFL._Meta.Property      import Property

import _TFL.Accessor
import _TFL.Filter
import _TFL._Meta.Object

class _M_Permission_ (TFL._.Filter._Filter_S_.__class__) :

    @property
    def instance (cls) :
        return cls ()
    # end def instance

# end class _M_Permission_

class _Permission_ \
        (TFL.Meta.BaM (TFL._.Filter._Filter_S_, metaclass = _M_Permission_)) :

    _rank         = 0
    auth_required = True

    @Property
    def instance (self) :
        return self
    # end def instance

    def message (self, user, page, * args, ** kw) :
        pass
    # end def message

    def _get_obj (self, page, kw) :
        result = kw.get ("obj")
        if result is None :
            result = getattr (page, "obj", None)
        return result
    # end def _get_obj

# end class _Permission_

class _User_Matches_Attribute_ (_Permission_) :
    """Permission if user matches the value of an attribute of the object associated with the resource"""

    attr_name = None

    def __init__ (self, attr_name = None) :
        if attr_name is not None :
            self.attr_name = attr_name
    # end def __init__

    def predicate (self, user, page, * args, ** kw) :
        if user :
            obj = self._get_obj (page, kw)
            if obj is not None :
                value = self._get_attribute (obj)
                return self._test (value, user)
    # end def predicate

    def _get_attribute (self, obj) :
        getter = getattr (TFL.Getter, self.attr_name)
        try :
            return getter (obj)
        except AttributeError :
            pass
    # end def _get_attribute

    def _test (self, value, user) :
        return value == user
    # end def _test

# end class _User_Matches_Attribute_

class _User_Person_Matches_Attribute_ (_User_Matches_Attribute_) :
    """Permission if user.person matches the value of an attribute of the object associated with the resource"""

    def _test (self, value, user) :
        return value == user.person
    # end def _test

# end class _User_Person_Matches_Attribute_

class In_Group (_Permission_) :
    """Permission if user is member of group"""

    def __init__ (self, name) :
        self.name = name
    # end def __init__

    def group (self, page) :
        scope = page.top.scope
        Group = scope ["Auth.Group"]
        return Group.instance (self.name)
    # end def group

    def predicate (self, user, page, * args, ** kw) :
        if user :
            group = self.group (page)
            return group in user.groups
    # end def predicate

# end class In_Group

class Is_Creator (_User_Matches_Attribute_) :
    """Permission if user is the creator of the object associated with the resource"""

    attr_name = "created_by"

# end class Is_Creator

class Is_Superuser (_Permission_) :
    """Permission if user is superuser"""

    def predicate (self, user, page, * args, ** kw) :
        return user and user.superuser
    # end def predicate

# end class Is_Superuser

class Login_has_Person (_Permission_) :
    """Permission if user has an associated person"""

    def predicate (self, user, page, * args, ** kw) :
        if user :
            return user.person is not None
    # end def predicate

# end class Login_has_Person

if __name__ != "__main__":
    GTW.RST._Export \
        ( "*"
        , "_Permission_"
        , "_User_Matches_Attribute_"
        , "_User_Person_Matches_Attribute_"
        )
### __END__ GTW.RST.Permission
