# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DB_Meta_Data
#
# Purpose
#    Provide meta data for MOM data base
#
# Revision Dates
#    30-Jun-2010 (CT) Creation (factored from `MOM.DBW.HPS.DB_Meta_Data`)
#    13-Aug-2010 (CT) `COPY` changed to set `readonly` to `False`
#    16-Aug-2010 (CT) `COPY` changed to use `_copy_ignore` and `NEW`
#    16-Aug-2010 (CT) `NEW`  changed to pop from `kw`
#    30-Jan-2011 (CT) `dbid` added
#    20-Jul-2011 (CT) Use `datetime.utcnow` instead of `datetime.now`
#     7-Jun-2013 (CT) Change `COPY` to iterate over `other`, not `other._kw`
#    12-Oct-2015 (CT) Add Python-3 future imports
#    16-Feb-2016 (CT) Store `root_pid`, not `root_epk`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM       import MOM
from   _TFL       import TFL

from   _TFL.pyk   import pyk

import _TFL.Environment
import _TFL.Record

import datetime
import uuid

class _MOM_DB_Meta_Data_ (TFL.Record) :
    """Provide meta data for MOM data base."""

    _real_name   = "DB_Meta_Data"
    _properties  = set (TFL.Record._properties)
    _copy_ignore = set (("readonly", "dbid", "dbv_hash"))

    @classmethod
    def COPY (cls, other, app_type, scope = None) :
        ignore = cls._copy_ignore | other._copy_ignore
        return cls.NEW \
            ( app_type, scope
            , ** dict ((k, other [k]) for k in other if k not in ignore)
            )
    # end def COPY

    @classmethod
    def NEW (cls, app_type, scope = None, ** _kw) :
        kw      = dict (_kw)
        Version = app_type.Version
        result  = cls \
            ( creator       = kw.pop ("creator", None) or TFL.Record
                ( date          = pyk.decoded (datetime.datetime.utcnow ())
                , tool_version  = Version.id
                , user          =
                    getattr (scope, "user", None) or TFL.Environment.username
                )
            , dbid          = pyk.decoded (uuid.uuid4 ())
            , dbv_hash      = app_type.db_version_hash
            , guid          =
                kw.pop ("guid", None) or getattr (scope, "guid", None)
            , readonly      = kw.pop  ("readonly", False)
            , root_pid      =
                kw.pop ("root_pid", None) or getattr (scope, "_root_pid", None)
            , ** kw
            )
        return result
    # end def NEW

DB_Meta_Data = _MOM_DB_Meta_Data_ # end class

if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.DB_Meta_Data
