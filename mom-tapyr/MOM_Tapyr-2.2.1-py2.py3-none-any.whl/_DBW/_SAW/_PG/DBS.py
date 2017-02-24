# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.PG.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.PG.DBS
#
# Purpose
#    Encapsulate PostgreSQL-specific functionality for SAW
#
# Revision Dates
#    24-Jun-2013 (CT) Creation
#    17-Jul-2013 (CT) Remove dependency on `MOM.DBW.SAS`
#    23-Aug-2013 (CT) Remove SAS-compatibility kludge `sa_scheme`
#     2-Sep-2014 (CT) Quote database name in `CREATE DATABASE` statement
#     6-Sep-2016 (CT) Use `template1`, not `template0`, as `template` default
#                     * corresponding to PostgreSQL documentation
#    ««revision-date»»···
#--

from   __future__          import division, print_function
from   __future__          import absolute_import, unicode_literals

from   _MOM                import MOM
from   _TFL                import TFL

from   _TFL.pyk            import pyk

from   _MOM._DBW._SAW      import SA

import _MOM._DBW._SAW.DBS

import contextlib

try :
    import psycopg2.extensions as PE
except ImportError :
    PE = None ### looks like PostgreSQL python adapter is not installed

class PG_DBS (MOM.DBW.SAW._NFB_DBS_) :
    """Encapsulate PostgreSQL-specific functionality for SAW"""

    _real_name             = "DBS"

    ISOLATION_AUTO_COMMIT  = getattr (PE, "ISOLATION_LEVEL_AUTOCOMMIT",   -1)
    ISOLATION_SERIALIZABLE = getattr (PE, "ISOLATION_LEVEL_SERIALIZABLE", -1)

    scheme                 = "postgresql"

    @classmethod
    def connect_change_isolation_level \
            (cls, connection, con_record, isolation_level) :
        connection.set_isolation_level (isolation_level)
    # end def connect_change_isolation_level

    @classmethod
    def create_engine (cls, db_url, isolation_level = None) :
        if isolation_level is None :
            isolation_level = cls.ISOLATION_SERIALIZABLE
        def _set_isolation_level (dbapi_connection, connection_record) :
            dbapi_connection.set_isolation_level (isolation_level)
        result = super (PG_DBS, cls).create_engine (db_url)
        SA.event.listen (result.engine, "connect", _set_isolation_level)
        return result
    # end def create_engine

    class Connection (object) :
        """Special auto-committing connection used for create database and
           drop database, only.
        """

        def __init__ (self, db_url, dbs) :
            engine = dbs.create_engine \
                ( TFL.Url (db_url.scheme_auth + "/postgres")
                , isolation_level = dbs.ISOLATION_AUTO_COMMIT
                )
            self.engine = engine
            self.conn   = engine.connect ()
        # end def __init__

        def execute (self, * args, ** kw) :
            return self.conn.execute (* args, ** kw)
        # end def execute

        def close (self) :
            self.conn.close   ()
            self.engine.close ()
        # end def close

    # end class Connection

    @classmethod
    def create_database \
            ( cls, db_url, manager
            , encoding = "utf8"
            , template = "template1"
            ) :
        conn = cls.Connection (db_url, cls)
        with contextlib.closing (conn) :
            ### before we try to create the database let's check if it does
            ### not already exist
            result = conn.execute \
                ( "SELECT datname FROM pg_database WHERE datname = %r"
                % (str (db_url.path), )
                ).fetchall ()
            if not result :
                ### database does not exist -> create it
                conn.execute \
                    ( """CREATE DATABASE "%s" ENCODING='%s' TEMPLATE %s"""
                    % (str (db_url.path), encoding, template)
                    )
    # end def create_database

    @classmethod
    def _drop_database (cls, db_url, manager) :
        conn = cls.Connection (db_url, cls)
        with contextlib.closing (conn) :
            conn.execute ("DROP DATABASE %s" % (str (db_url.path), ))
    # end def _drop_database

DBS = PG_DBS # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.PG._Export ("*")
### __END__ MOM.DBW.SAW.PG.DBS
