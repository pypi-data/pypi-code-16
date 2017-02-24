# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.EMS.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.EMS.SAW
#
# Purpose
#    Entity manager strategy using SQLAlchemy wrapped by SAW
#
# Revision Dates
#     4-Jul-2013 (CT) Creation
#     5-Jul-2013 (CT) Change sig of `_query_single_root`, `_query_multi_root`
#    16-Jul-2013 (CT) Add `pid_query` delegating to `.session.pid_query`
#    17-Jul-2013 (CT) Remove `db_cid`
#    21-Jul-2013 (CT) Cache `Q_Result` instances
#    30-Jul-2013 (CT) Change `changes` to call `filter` only if necessary
#     1-Aug-2013 (CT) Use `Q_Result.SCM_Change` for `changes`
#     2-Aug-2013 (CT) Change `changes` to be usable by `MOM.DB_Man`, too
#     5-Aug-2013 (CT) Move `Q_Result` to `MOM.DBW.SAW.Session`;
#                     use `.session.SCM_Change_Query`
#     5-Aug-2013 (CT) Add `rollback_pending_change`, `save_point` --> session
#    ««revision-date»»···
#--

from   __future__          import division, print_function
from   __future__          import absolute_import, unicode_literals

from   _MOM                import MOM
from   _TFL                import TFL
from   _TFL.pyk            import pyk

import _MOM.Entity
import _MOM.Error
import _MOM._EMS._Manager_

import _TFL._Meta.Once_Property

class Manager (MOM.EMS._Manager_) :
    """Entity manager using SQLAlchemy wrapped by SAW."""

    type_name               = "SAW"

    lazy_load_p             = True
    max_cid                 = property (TFL.Getter.session.max_cid)
    max_pid                 = property (TFL.Getter.session.max_pid)
    pcm                     = TFL.Meta.Alias_Property ("session")
    rollback_pending_change = property \
        (TFL.Getter.session.rollback_pending_change)
    save_point              = property (TFL.Getter.session.save_point)

    ### Because SAW has a separate table for `MOM.Id_Entity`, all queries are
    ### rooted in that table, even though it is not a `relevant_root`
    _query_multi_root       = _query_single_root = \
        TFL.Meta.Alias_Property ("Q_Result")

    @TFL.Meta.Once_Property
    def Q_Result (self) :
        return self.session.Q_Result
    # end def Q_Result

    def changes (self, * filters, ** eq_kw) :
        query = self.session.SCM_Change_Query
        if filters or eq_kw :
            query = query.filter (* filters, ** eq_kw)
        return query
    # end def changes

    def commit (self) :
        if self.uncommitted_changes :
            self.__super.commit ()
        else :
            ### do a session rollback to release DB resources
            self.session.rollback ()
    # end def commit

    def load_root (self) :
        result = self.session.load_root (self.scope)
        return result
    # end def load_root

    def pid_query (self, pid, Type = None) :
        return self.session.pid_query (int (pid), Type)
    # end def pid_query

    def register_change (self, change) :
        scope   = self.scope
        session = self.session
        session.add_change           (change)
        self.__super.register_change (change)
        session.update_change        (change)
    # end def register_change

    def register_scope (self) :
        self.session.register_scope (self.scope)
    # end def register_scope

    def rename (self, entity, new_epk, renamer) :
        old_entity = self.instance (entity.__class__, new_epk)
        if old_entity :
            raise MOM.Error.Name_Clash (entity, old_entity)
        renamer ()
    # end def rename

    def update (self, entity, change) :
        self.session.update (entity, change)
    # end def update

    def _add (self, entity, pid = None) :
        from _MOM._DBW._SAW import SA
        session = self.session
        max_c   = entity.max_count
        if max_c and max_c <= self.session.Q_Result (entity.E_Type).count () :
            raise MOM.Error.Too_Many_Objects (entity, entity.max_count)
        try :
            session.add (entity, pid)
        except SA.Exception.IntegrityError as exc :
            raise self.Integrity_Error (str (exc))
    # end def _add

    def _remove (self, entity) :
        self.session.delete (entity)
    # end def _remove

# end class Manager

if __name__ != "__main__" :
    MOM.EMS._Export_Module ()
### __END__ MOM.EMS.SAW
