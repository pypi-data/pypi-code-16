# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.DBW.HPS.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW.HPS.Pid_Manager
#
# Purpose
#    HPS specific manager for permanent ids
#
# Revision Dates
#    11-May-2010 (CT) Creation
#    11-May-2010 (MG) `ems` and `db_uri` added
#    12-May-2010 (CT) `retire` added
#    12-May-2010 (CT) `reserve` corrected (corner cases)
#     4-Aug-2012 (CT) Change `retire` not to set `pid` to None
#    30-Jan-2013 (CT) Add `zombies`
#    26-Aug-2013 (CT) Move `__call__` in here from `MOM.DBW.Pid_Manager`
#    ««revision-date»»···
#--

"""
Pid manager for Hash-Pickle-Store::

    >>> from _TFL.Record import Record as R
    >>> pm = Pid_Manager ()
    >>> pm.new (R ())
    1
    >>> pm.new (R ())
    2
    >>> pm.reserve (R (), 5)
    5
    >>> pm.reserve (R (), 5)
    Traceback (most recent call last):
      ...
    ValueError: Cannot reserve pid 5, already used by entity `Record (pid = 5)`
    >>> pm.new (R ())
    6
    >>> pm.max_pid
    6

"""

from   _MOM       import MOM
from   _TFL       import TFL

import _MOM._DBW._HPS
import _MOM._DBW.Pid_Manager

class Pid_Manager (MOM.DBW.Pid_Manager) :
    """HPS specific manager for permanent ids."""

    def __init__ (self, ems = None, db_url = None) :
        self.__super.__init__ (ems, db_url)
        self.max_pid = 0
        self.table   = {}
        self.zombies = {}
    # end def __init__

    def __call__ (self, entity, pid = None, ** kw) :
        if pid is None :
            pid = self.new (entity, ** kw)
        else :
            self.reserve (entity, pid, ** kw)
        return pid
    # end def __call__

    def flush_zombies (self) :
        self.zombies = {}
    # end def flush_zombies

    def new (self, entity) :
        self.max_pid += 1
        result = self.max_pid
        if entity is not None :
            self.table [result] = entity
            entity.pid = result
        return result
    # end def new

    def query (self, pid) :
        if pid in self.zombies :
            return self.zombies [pid]
        else :
            return self.table [pid]
    # end def query

    def reserve (self, entity, pid) :
        table = self.table
        if pid in table :
            if table [pid] is not entity :
                raise ValueError \
                    ( "Cannot reserve pid %s, already used by entity `%r`"
                    % (pid, table [pid])
                    )
        else :
            self.max_pid = max (pid, self.max_pid)
            if entity is not None :
                table [pid] = entity
                entity.pid  = pid
                self.zombies.pop (pid, None)
        return pid
    # end def reserve

    def retire (self, entity) :
        pid = entity.pid
        self.table.pop (pid, None)
        self.zombies [pid] = entity
    # end def retire

# end class Pid_Manager

if __name__ != "__main__" :
    MOM.DBW.HPS._Export ("*")
### __END__ MOM.DBW.HPS.Pid_Manager
