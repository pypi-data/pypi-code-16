# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.DBW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW._DBS_
#
# Purpose
#    Encapsulate db-specific functionality
#
# Revision Dates
#    23-Jun-2010 (CT) Creation
#    30-Nov-2010 (CT) `Fatal_Exceptions` added (here, an empty tuple)
#    14-Jun-2011 (MG) `url` add the `query` of the `db_url` to
#                     `scheme_auth` (to allow specification of the the mysql
#                     socket file)
#    15-Jun-2011 (MG) `url` fixed (only add `query` if it is not empty)
#    27-Apr-2012 (MG) `reserve_cid` added
#    ««revision-date»»···
#--

from   _MOM                      import MOM
from   _TFL                      import TFL
from   _TFL                      import sos

import _MOM._DBW._Manager_

import _TFL._Meta.Object
import _TFL.Url

class _M_DBS_ (TFL.Meta.Object.__class__) :
    """Meta class for DBS classes."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if not name.startswith ("_") :
            MOM.DBW._Manager_.DBS_map [cls.scheme] = cls
    # end def __init__

# end class _M_DBS_

class _DBS_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _M_DBS_)) :
    """Base class for DBS classes."""

    Fatal_Exceptions = ()

    @classmethod
    def create_database (cls, db_url, manager) :
        pass
    # end def create_database

    @classmethod
    def delete_database (cls, db_url, manager) :
        try :
            sos.unlink (db_url.path)
        except OSError :
            pass
    # end def delete_database

    @classmethod
    def reserve_cid (cls, connection, cid) :
        pass
    # end def reserve_cid

    @classmethod
    def reserve_pid (cls, connection, pid) :
        pass
    # end def reserve_pid

    @classmethod
    def Url (cls, value, ANS, default_path = None) :
        result = TFL.Url (value, fs_path = True)
        if not result.path and default_path is not None :
            result = TFL.Url.new (result, path = default_path, fs_path = True)
        result.scheme_auth = "://".join ((result.scheme, result.authority))
        if result.query :
            result.scheme_auth = "?".join ((result.scheme_auth, result.query))
        result.create = False
        return result
    # end def Url

# end class _DBS_

if __name__ != "__main__" :
    MOM.DBW._Export ("_DBS_")
### __END__ MOM.DBW._DBS_
