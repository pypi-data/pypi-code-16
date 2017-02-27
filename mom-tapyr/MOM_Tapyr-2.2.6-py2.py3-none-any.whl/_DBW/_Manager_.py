# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014 Martin Glueck. All rights reserved
# Langstrasse 4, 2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW._Manager_
#
# Purpose
#    Base class for database backend specific _Manager_ classes
#
# Revision Dates
#    19-Oct-2009 (MG) Creation
#    30-Nov-2009 (CT) `update_etype` added
#     4-Dec-2009 (MG) Renamed from `Session` to `_Manager_`
#    16-Dec-2009 (MG) `_Manager_.prepare` added
#    27-Jan-2010 (MG) `update_etype` parameter `app_type` added
#    11-May-2010 (CT) `Pid_Manager` added
#    23-Jun-2010 (CT) `DBS_map` added
#     9-Sep-2012 (CT) Add `_commit_creation_change`
#    31-Jan-2013 (MG) Add `finalize`
#     9-Apr-2013 (CT) Add `db_sig`
#    19-Jun-2013 (CT) Add `delete_database`; use `@subclass_responsibility`
#    24-Jun-2013 (CT) Add argument `app_type` to `prepare`
#    24-Jun-2013 (CT) Add missing methods-stubs to `_Manager_`
#     8-Jul-2013 (CT) Add argument `app_type` to `finalize`
#    ««revision-date»»···
#--

from   _TFL       import TFL
from   _MOM       import MOM

import _MOM._DBW
import _MOM._DBW.Pid_Manager

import _TFL._Meta.Object

from   _TFL.Decorator    import subclass_responsibility

class _M_Manager_ (TFL.Meta.Object.__class__) :
    """Backend independent _Manager_, describes the common interface."""

    DBS_map = {}
    db_sig  = ()

    @subclass_responsibility
    def connect_database (cls, db_url, scope) :
        pass
    # end def connect_database

    @subclass_responsibility
    def create_database (cls, db_url, scope) :
        pass
    # end def create_database

    @subclass_responsibility
    def delete_database (cls, db_url) :
        pass
    # end def delete_database

    def etype_decorator (cls, e_type) :
        return e_type
    # end def etype_decorator

    def finalize (cls, app_type) :
        pass
    # end def finalize

    def prepare (cls, app_type) :
        pass
    # end def prepare

    def update_etype (cls, e_type, app_type) :
        pass
    # end def update_etype

# end class _M_Manager_

class _Manager_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _M_Manager_)) :
    """Base class for database backend specific _Manager_ classes"""

    Pid_Manager      = MOM.DBW.Pid_Manager
    type_name        = "Bare"

    @subclass_responsibility
    def change_readonly (self, state) :
        pass
    # end def change_readonly

    @subclass_responsibility
    def close (self) :
        pass
    # end def close

    def close_connections (self) :
        pass ### redefine as necessary for descendents
    # end def close_connections

    @subclass_responsibility
    def commit (self) :
        pass
    # end def commit

    def compact (self) :
        pass ### redefine as necessary for descendents
    # end def compact

    def rollback (self, keep_zombies = False) :
        pass ### Nothing needs to be done here
    # end def rollback

    def _commit_creation_change (self, cc, kw) :
        pass ### redefine as necessary for descendents
    # end def _commit_creation_change

# end class _Manager_

if __name__ != '__main__':
    MOM.DBW._Export ("_Manager_")
### __END__ MOM.DBW._Manager_
