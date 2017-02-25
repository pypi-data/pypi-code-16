# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.Session
#
# Purpose
#    Base class for sessions.
#
# Revision Dates
#    25-Jan-2010 (MG) Creation
#    19-Feb-2010 (MG) Moved from `GTW.Tornado` into `GTW`
#    20-Feb-2010 (MG) `__contains__` added
#     5-Aug-2010 (MG) `New_ID` factored from `_new_sid`, `setdefault` added
#     8-Aug-2010 (MG) `setdefault` added
#    10-Mar-2011 (CT) `__setattr__` added
#    11-Mar-2011 (CT) `Login`, `expiry`, `hash`, and `username` added
#     2-May-2011 (CT) `edit_session` and `new_edit_session` changed to
#                     support `hard_expiry` and `soft_expiry`
#    11-May-2011 (MG) `Session.__init__`: create new sid of passed `sid` does
#                     not exists
#                     `renew_session_id` added
#    11-May-2011 (MG) Alphabatically sorted
#     5-Apr-2012 (CT) Sort alphabetically, `_...` at end,
#                     properties right after `__init__`
#     5-Apr-2012 (CT) Add stubs for `remove` and `save`
#     5-Apr-2012 (CT) Rename `Login` to `User`
#    26-Apr-2012 (CT) Change `_date` to create `User()` if `._load` returns `{}`
#    23-Jul-2012 (CT) Call `renew_session_id` in `username.setter`
#     4-Aug-2012 (MG) Don't save session on session id renewal
#    19-Aug-2012 (MG) Add repr for User class
#     2-May-2013 (CT) Convert `New_ID` to instance method,
#                     use `settings ["hash_fct"]`, if any
#     5-May-2013 (CT) Add change guard to `username.setter`
#    11-Dec-2013 (CT) Fix `_data` to check user *only* once after `_load ()`
#    11-Feb-2014 (CT) Force `sid` to `str`
#     2-Jul-2014 (CT) Localize `Epxired` message
#    12-Oct-2014 (CT) Use `TFL.Secure_Hash`
#    11-Dec-2014 (CT) Add `User.change`, `.is_valid`; remove `User.name.setter`
#    11-Dec-2014 (CT) Keep sessions that are expired or invalid but ignore
#                     `user.name` of such sessions
#    11-Dec-2014 (CT) Don't change session ids, remove `renew_session_id`
#    11-Dec-2014 (CT) Use `uuid4` for session id
#    26-Jan-2015 (CT) Derive `M_Session` from `M_Auto_Update_Combined`,
#                     not `M_Auto_Combine_Sets`
#    13-Mar-2015 (CT) Don't return False from `username`
#    10-Jun-2015 (CT) Import `M_Auto_Update_Combined`, not `M_Auto_Combine_Sets`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   _GTW                     import GTW

from   _TFL                     import TFL
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object
import _TFL._Meta.M_Auto_Update_Combined
import _TFL.User_Config

import base64
import datetime
import os
import random
import time
import uuid

@pyk.adapt__bool__
class User (TFL.Meta.Object) :
    """Encapsulate user information for session."""

    expired        = True
    expiry         = None
    hash           = None
    valid_hash     = False

    _name          = None

    def __init__ (self) :
        self._name    = None
        self.sessions = {}
    # end def __init__

    @property
    def is_valid (self) :
        return self._name and self.valid_hash and not self.expired
    # end def is_valid

    @property
    def name (self) :
        return self._name
    # end def name

    def change (self, name, hash, expiry) :
        invalid         = name is None
        self.expired    = invalid
        self.expiry     = expiry
        self.hash       = hash
        self.valid_hash = not invalid
        self._name      = name
    # end def change

    def __bool__ (self) :
        return self._name is not None
    # end def __bool__

    def __repr__ (self) :
        return "GTW.Session.User (%s)" % self._name
    # end def __repr__

# end class User

class M_Session (TFL.Meta.M_Auto_Update_Combined) :
    """Meta class for Session."""

# end class M_Session

@pyk.adapt__bool__
class Session (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Session)) :
    """Base class for sessions

       >>> from _GTW.Memory_Session import Memory_Session
       >>> session  = Memory_Session (None, dict (cookie_salt = "salt"))
       >>> session2 = Memory_Session (None, dict (cookie_salt = "salt"))
       >>> session.sid != session2.sid
       True
    """

    _data_dict         = None
    _non_data_attrs    = set \
        (("_data", "_data_dict", "_hasher", "_sid", "_settings", "username"))
    _attrs_to_update_combine = ("_non_data_attrs", )

    class Expired (LookupError) :
        pass
    # end class Expired

    def __init__ (self, sid = None, settings = {}, hasher = None) :
        self._settings = settings
        self._hasher   = hasher or (lambda x : x)
        if sid is None :
            self._sid  = self._new_sid (settings.get ("cookie_salt"))
            self._data = dict (user = User ())
        else :
            self._sid  = str (sid)
    # end def __init__

    @property
    def sid (self) :
        return self._sid
    # end def sid

    @property
    def username (self) :
        user = self.user
        return user.name if user.is_valid else None
    # end def username

    @username.setter
    def username (self, value) :
        self._change_user (self.user, value)
    # end def username

    @property
    @getattr_safe
    def _data (self) :
        loaded = False
        result = self._data_dict
        if result is None :
            result = self._data_dict = loaded = self._load ()
            user   = result.get ("user")
            if user is None :
                user = result ["user"] = User ()
            user.expired    = self._expired (user.expiry)
            user.valid_hash = (user.hash == self._hasher (user.name))
            if loaded :
                for id in list (user.sessions) :
                    try :
                        self.edit_session (id)
                    except LookupError :
                        pass
        return result
    # end def _data

    @_data.setter
    def _data (self, value) :
        self._data_dict = value
    # end def _data

    def edit_session (self, id) :
        user = self.user
        data = user.sessions [id]
        if len (data) == 2 :
            hard_expiry, soft_expiry, hash = data [0], None, data [1]
        else :
            hard_expiry, soft_expiry, hash = data
        if self._expired (hard_expiry) :
            user.sessions.pop (id, None)
            raise LookupError \
                ( "Edit session expired since %s"
                % (hard_expiry.strftime ("%Y/%m/%d %H:%M"), )
                )
        if soft_expiry and self._expired (soft_expiry) :
            raise self.Expired \
                ( _T ("Edit session expired since %s")
                % (soft_expiry.strftime ("%Y/%m/%d %H:%M"), )
                )
        return hash
    # end def edit_session

    def exists (self, sid) :
        raise NotImplementedError \
            ("%s must implement `exists`" % (self.__class__, ))
    # end def exists

    def get (self, key, default = None) :
        return self._data.get (key, default)
    # end def get

    def new_edit_session (self, hash_sig, ttl = None) :
        assert self.user
        hard_expiry = self._expiry (ttl, "user_session_ttl")
        soft_expiry = self._expiry (ttl, "edit_session_ttl")
        hash_fct    = self._settings.get ("hash_fct", TFL.user_config.sha)
        id          = uuid.uuid4 ().hex
        hash        = \
            hash_fct ((hash_sig, hard_expiry, soft_expiry)).b64digest ()
        self.user.sessions [id] = (hard_expiry, soft_expiry, hash)
        return id, hash
    # end def new_edit_session

    def New_ID (self, check = None, salt = "") :
        hash_fct = self._settings.get ("hash_fct", TFL.user_config.sha)
        while True :
            id = hash_fct ("%s%s" % (uuid.uuid4 ().hex, salt)).hexdigest ()
            if check is None or not check (id) :
                return pyk.text_type (id)
    # end def New_ID

    def pop (self, name, default = None) :
        return self._data.pop (name, default)
    # end def pop

    def pop_edit_session (self, id) :
        return self.user.sessions.pop (id, (None, )) [-1]
    # end def pop_edit_session

    def remove (self) :
        raise NotImplementedError \
            ("%s must implement `remove`" % (self.__class__, ))
    # end def remove

    def save (self) :
        raise NotImplementedError \
            ("%s must implement `save`" % (self.__class__, ))
    # end def save

    def setdefault (self, key, default = None) :
        if key not in self._data :
            self._data [key] = default
        return self._data [key]
    # end def setdefault

    def _change_user (self, user, value) :
        user.change \
            ( name   = value
            , hash   = self._hasher (value)
            , expiry = None if value is None else self._expiry ()
            )
    # end def _change_user

    def _expired (self, expiry) :
        if expiry :
            return datetime.datetime.utcnow () > expiry
    # end def _expired

    def _expiry (self, ttl = None, ttl_name = "user_session_ttl") :
        if ttl is None :
            ttl = self._settings.get (ttl_name, 3600)
        if not isinstance (ttl, datetime.timedelta) :
            ttl  = datetime.timedelta (seconds = ttl)
        return datetime.datetime.utcnow () + ttl
    # end def _expiry

    def _new_sid (self, salt) :
        return self.New_ID (self.exists, salt)
    # end def _new_sid

    def __bool__ (self) :
        return any (bool (v) for v in pyk.itervalues (self._data))
    # end def __bool__

    def __contains__ (self, item) :
        return item in self._data
    # end def __contains__

    def __delattr__ (self, name) :
        del self [name]
    # end def

    def __delitem__ (self, key) :
        self._data.pop (key, None)
    # end def __delitem__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self.get (name)
    # end def __getattr__

    def __getitem__ (self, key) :
        return self._data [key]
    # end def __getitem__

    def __setattr__ (self, name, value) :
        if name in self._non_data_attrs :
            return self.__super.__setattr__ (name, value)
        else :
            self._data [name] = value
            return value
    # end def __setattr__

    def __setitem__ (self, key, value) :
        self._data [key] = value
    # end def __setitem__

# end class Session

if __name__ != "__main__" :
    GTW._Export ("Session")
### __END__ GTW.Session
