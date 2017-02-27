# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.DBS
#
# Purpose
#    Encapsulate db-specific functionality for SAW
#
# Revision Dates
#    19-Jun-2013 (CT) Creation
#    24-Jun-2013 (CT) Factor db-specific specific classes into sub-packages
#    17-Jul-2013 (CT) Remove dependency on `MOM.DBW.SAS`
#    31-Jul-2013 (CT) Factor `close_connections` from `close`
#    31-Jul-2013 (CT) Add `Con_Man`, `con_man`, and `con_man_seq`;
#                     remove `commit`, `rollback`, `commit_pid`,
#                     `connection_pid`, and `rollback_pid`
#     1-Aug-2013 (CT) Change `DBS.close` and `DBS.close_connections` to deal
#                     with `Con_Man` instances
#     5-Aug-2013 (CT) Change guard of `connection`, reset `needs_commit` there
#     5-Aug-2013 (CT) Add `Con_Man.save_point`, factor `Con_Man._reset`
#    23-Aug-2013 (CT) Remove SAS-compatibility kludge `sa_url`
#    ««revision-date»»···
#--

from   __future__                import division, print_function
from   __future__                import absolute_import, unicode_literals

from   _MOM                      import MOM
from   _TFL                      import TFL
from   _TFL.pyk                  import pyk

from   _MOM._DBW._SAW            import SA

import _MOM._DBW._DBS_

import _TFL._Meta.Object
import _TFL._Meta.Property

import contextlib

@pyk.adapt__bool__
class Save_Point (TFL.Meta.Object) :

    def __init__ (self, con_man) :
        self.con_man    = con_man
        self.level      = 0
        self.save_point = con_man.connection.begin_nested ()
    # end def __init__

    def commit (self) :
        self.level -= 1
        if self.level < 0 :
            self._destroy ()
    # end def commit

    def rollback (self) :
        if self.save_point is not None :
            self.save_point.rollback ()
            self._destroy            ()
    # end def rollback

    def _destroy (self) :
        self.con_man._save_point = None
        self.con_man             = None
        self.level               = -1
        self.save_point          = None
    # end def _destroy

    def __bool__ (self) :
        return self.save_point is not None
    # end def __bool__

# end class Save_Point

class Con_Man (TFL.Meta.Object) :
    """Manage a sqlalchemy connection and a related transaction."""

    Save_Point   = Save_Point

    needs_commit = False
    transaction  = None
    _save_point  = None

    def __init__ (self, engine) :
        self.engine = engine
    # end def __init__

    @TFL.Meta.Once_Property
    def connection (self) :
        assert self.transaction is None
        result = self.engine.connect ()
        self._reset (transaction = result.begin ())
        return result
    # end def connection

    def close (self) :
        self.engine = None
    # end def close

    def commit (self) :
        self._close_connection (TFL.Method.commit)
    # end def commit

    def rollback (self) :
        self._close_connection (TFL.Method.rollback)
    # end def rollback

    def save_point (self) :
        result = self._save_point
        if result is None :
            return self.Save_Point (self)
        else :
            result.level += 1
        return result
    # end def save_point

    def _close_connection (self, trans_method) :
        dct         = self.__dict__
        connection  = dct.get ("connection")
        transaction = self.transaction
        try :
            if transaction is not None :
                trans_method (transaction)
            if connection is not None :
                connection.close ()
        finally :
            self._reset ()
            dct.pop ("connection", None)
    # end def _close_connection

    def _reset (self, transaction = None) :
        self.needs_commit = False
        self.transaction  = transaction
        self._save_point  = None
    # end def _reset

# end class Con_Man

class _SAW_DBS_ (MOM.DBW._DBS_) :
    """Base class for SAW DBS classes"""

    _real_name                = "DBS"

    Commit_Conflict_Exception = SA.Exception.DBAPIError
    Con_Man                   = Con_Man
    Con_Man_Seq               = Con_Man
    Engine_Parameter          = dict (pool_recycle = 900, echo = False)

    default_url               = None
    echo                      = TFL.Meta.Alias_Property ("_sa_engine.echo")
    query_last_cid_on_update  = False
    table_kw                  = {}

    def __init__ (self, sa_engine) :
        self._sa_engine = sa_engine
    # end def __init__

    @classmethod
    def create_engine (cls, db_url, ** kw) :
        url       = db_url.value or cls.default_url
        ekw       = dict (cls.Engine_Parameter, ** kw)
        sa_engine = SA.engine.create_engine (url, ** ekw)
        return cls (sa_engine)
    # end def create_engine

    @TFL.Meta.Once_Property
    def con_man (self) :
        return self.Con_Man (self)
    # end def con_man

    @TFL.Meta.Once_Property
    def con_man_seq (self) :
        return self.Con_Man_Seq (self)
    # end def con_man_seq

    def connect (self) :
        return self._sa_engine.connect ()
    # end def connect

    def close (self) :
        for con_man in self.con_man, self.con_man_seq :
            try :
                con_man.close ()
            except Exception as exc :
                pass
        self._sa_engine = None
        self.__dict__.pop ("con_man",     None)
        self.__dict__.pop ("con_man_seq", None)
    # end def close

    def close_connections (self) :
        for con_man in self.con_man, self.con_man_seq :
            try :
                con_man.rollback ()
            except Exception as exc :
                pass
        self._sa_engine.pool.dispose ()
    # end def close_connections

    def create_tables (self, metadata) :
        metadata.create_all (self._sa_engine)
    # end def create_tables

    @classmethod
    @TFL.Contextmanager
    def rollback_context (cls, scope, session) :
        yield
    # end def rollback_context

    def __getattr__ (self, name) :
        return getattr (self._sa_engine, name)
    # end def __getattr__

DBS = _SAW_DBS_ # end class

class _NFB_DBS_ (_SAW_DBS_) :
    """Base class for non-file based databases."""

    Fatal_Exceptions = (SA.Exception.OperationalError, )
    pm               = None

    @classmethod
    def delete_database (cls, db_url, manager) :
        try :
            cls._drop_database (db_url, manager)
        except SA.Exception.DBAPIError as e:
            ### looks like we don't have the permissions to drop the database
            ### -> let's delete all tables we find using the reflection
            ### mechanism of sqlalchemy
            engine = cls.create_engine (db_url)
            meta   = SA.MetaData       (bind = engine)
            try :
                meta.reflect ()
                if meta.tables :
                    cls._drop_database_content (engine, meta)
            except SA.Exception.DBAPIError :
                pass
            engine.close ()
    # end def delete_database

    @classmethod
    def Url (cls, value, ANS, default_path = None) :
        if default_path :
            default_path = TFL.Filename (default_path).base
        return super (_NFB_DBS_, cls).Url (value, ANS, default_path)
    # end def Url

    @classmethod
    def _drop_database_content (cls, engine, meta) :
        meta.drop_all ()
    # end def _drop_database_content

# end class _NFB_DBS_

if __name__ != "__main__" :
    MOM.DBW.SAW._Export ("*", "_NFB_DBS_")
### __END__ MOM.DBW.SAW.DBS
