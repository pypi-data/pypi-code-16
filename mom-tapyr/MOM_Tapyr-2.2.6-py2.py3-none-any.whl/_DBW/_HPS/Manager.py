# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW.HPS.Manager
#
# Purpose
#    Database wrapper for Hash-Pickle-Store
#
# Revision Dates
#    18-Dec-2009 (CT) Creation
#    21-Dec-2009 (CT) Creation continued
#    19-Jan-2010 (CT) `rollback` added
#    20-Jan-2010 (CT) Provide `info` even if there is no `store`
#     2-Feb-2010 (CT) `commit` changed to update `info.max_cid`  even if
#                     there is no `store`
#     4-Mar-2010 (CT) `_new_manager` factored; `delete_database` added
#    11-May-2010 (CT) `Pid_Manager` added
#    18-May-2010 (CT) `Change_Manager` and `load_changes` added
#    23-Jun-2010 (CT) Import for `_MOM._DBW._HPS.DBS` added
#    30-Jun-2010 (CT) `_new_manager` changed to use `scope.ilk`
#    30-Jun-2010 (CT) `db_meta_data` added
#    30-Jun-2010 (CT) `change_readonly` added
#    30-Jun-2010 (CT) `pcm` added
#     1-Jul-2010 (CT) `compact` added
#    22-Jun-2012 (MG) `close_connections` added
#    30-Jan-2013 (CT) Add optional argument `keep_zombies` to `rollback`
#     6-Jun-2013 (CT) Add `max_surrs`
#    24-Jun-2013 (CT) Factor `close_connections`, `rollback` to `DBW._Manager_`
#    25-Aug-2013 (CT) Redefine `update_etype` to disable `P_uniqueness [0]`
#    ««revision-date»»···
#--

from   _MOM       import MOM
from   _TFL       import TFL

import _MOM._DBW._HPS.Change_Manager
import _MOM._DBW._HPS.DBS
import _MOM._DBW._HPS.Pid_Manager
import _MOM._DBW._HPS.Store
import _MOM._DBW._Manager_

from   _TFL import sos

import _TFL.Accessor
import _TFL.Filename

class _M_HPS_Manager_ (MOM.DBW._Manager_.__class__) :
    """Meta class for MOM.DBW.HPS.Manager"""

    def connect_database (cls, db_url, scope) :
        return cls._new_manager (db_url, scope, TFL.Method.load_info)
    # end def connect_database

    def create_database (cls, db_url, scope) :
        return cls._new_manager (db_url, scope, TFL.Method.create)
    # end def create_database

    def delete_database (cls, db_url) :
        uri = db_url.path
        try :
            sos.unlink (uri)
        except OSError :
            pass
        x_uri = MOM.DBW.HPS.Store.X_Uri (uri).name
        try :
            sos.rmdir (x_uri, True)
        except OSError :
            pass
    # end def delete_database

    def update_etype (cls, e_type, app_type) :
        try :
            e_type.P_uniqueness [0].ems_check = False
        except Exception :
            pass
    # end def update_etype

    def _new_manager (cls, db_url, scope, store_fct) :
        store = None
        uri   = db_url and db_url.path
        if uri :
            Store = getattr (MOM.DBW.HPS, "Store_%s" % scope.ilk)
            store = Store   (TFL.Filename (uri), scope)
            store_fct       (store)
        return cls (store, scope)
    # end def _new_manager

# end class _M_HPS_Manager_

class Manager (TFL.Meta.BaM (MOM.DBW._Manager_, metaclass = _M_HPS_Manager_)) :
    """Database wrapper for Hash-Pickle-Store."""

    Pid_Manager   = MOM.DBW.HPS.Pid_Manager

    db_meta_data  = TFL.Meta.Alias_Property ("info")
    pcm           = TFL.Meta.Alias_Property ("store")
    readonly      = property (TFL.Getter.info.readonly)

    type_name     = "HPS"

    def __init__ (self, store, scope) :
        self.store = store
        self.scope = scope
        if store is None :
            self._info = MOM.DBW.HPS.DB_Meta_Data.NEW (scope.app_type, scope)
            self.cm    = MOM.DBW.HPS.Change_Manager   ()
        else :
            self.cm    = store.cm
    # end def __init__

    def change_readonly (self, state) :
        if self.store is not None :
            self.store.change_readonly (state)
    # end def change_readonly

    def close (self) :
        if self.store is not None :
            self.store.close ()
    # end def close

    def commit (self) :
        if self.store is not None :
            self.store.commit ()
        else :
            info           = self._info
            ems            = self.scope.ems
            info.max_cid   = ems.max_cid
            info.max_pid   = ems.max_pid
            info.max_surrs = ems.max_surrs
    # end def commit

    def compact (self) :
        if self.store is not None :
            self.store.compact ()
    # end def compact

    @property
    def info (self) :
        if self.store is not None :
            return self.store.info
        else :
            return self._info
    # end def info

    def load_changes (self) :
        if self.store is not None :
            self.store.load_changes ()
    # end def load_changes

    def load_objects (self) :
        if self.store is not None :
            self.store.load_objects ()
    # end def load_objects

# end class Manager

if __name__ != '__main__':
    MOM.DBW.HPS._Export ("*")
### __END__ MOM.DBW.HPS.Manager
