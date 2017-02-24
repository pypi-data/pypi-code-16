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
#    MOM.DBW.SAW.Sequence
#
# Purpose
#    Wrap or emulate a database sequence
#
# Revision Dates
#    24-Jun-2013 (CT) Creation
#     8-Jul-2013 (CT) Change signature of `Sequence` to `attr`, not `attr_name`
#     8-Jul-2013 (CT) Use `.ATW.SA_Type.sized_int_type`, not `SA.types.Integer`
#    17-Jul-2013 (CT) Add argument `session` to methods needing that
#    26-Jul-2013 (CT) Add guard to `reserve`
#    26-Jul-2013 (CT) Factor `_reserve` to improve redefinability by descendents
#    28-Jul-2013 (CT) Change `seq_name` to lower case, remove `.`
#    31-Jul-2013 (CT) Use `scalar`, not `fetchone`, to extract col
#    31-Jul-2013 (CT) Use `session.con_man_seq`
#    31-Jul-2013 (CT) Change `reserve` to act only on `value > max_value`
#     1-Aug-2013 (CT) Update `session.seq_high`
#    26-Aug-2013 (CT) Split into `Sequence`, `Sequence_PID`, `Sequence_X`
#    29-Aug-2013 (CT) Add optional argument `force` to `reserve`
#    ««revision-date»»···
#--

from   __future__     import division, print_function
from   __future__     import absolute_import, unicode_literals

from   _MOM           import MOM
from   _TFL           import TFL

from   _TFL.pyk       import pyk

from   _MOM._DBW._SAW import SA

import _MOM._DBW
import _MOM._DBW._SAW.DBS
import _MOM._DBW._SAW.SA_Type

import _TFL._Meta.Object
import _TFL._Meta.Once_Property

class _Sequence_ (TFL.Meta.Object) :

    col_args            = ()
    sa_column           = None
    sa_seq              = None
    sa_table            = None
    table_name          = ""

    _column_kw          = {}
    _table_kw           = {}

    def __init__ (self, attr, ETW) :
        self.ATW        = ETW.ATW
        self.DBW        = DBW   = ETW.DBW
        self.ETW        = ETW
        self.PNS        = PNS   = ETW.PNS
        self.dbs        = PNS.DBS
        self.attr       = attr
        self.name       = attr.name
        self.e_type     = e_type = ETW.e_type
        self.type_name  = e_type.type_name
        self.seq_name   = \
            ("%s_%s_seq" % (e_type._saw_table_name (DBW), attr.name))
    # end def __init__

    def commit (self, session) :
        pass
    # end def commit

    def close (self, session) :
        pass
    # end def close

    def extract (self, session, entity, kw, sa_result) :
        pass
    # end def extract

    def insert (self, session, entity, spks, kw) :
        attr  = self.attr
        v     = attr.get_value (entity)
        spk   = spks.get (attr.name)
        if spk is not None :
            if v is None :
                v = spk
            elif v != spk :
                raise TypeError \
                    ( "Cannot pass %s %s when entity already has %s"
                    % (attr.name, spk, v)
                    )
        if v is None :
            v = self.next_value (session)
            if v is not None :
                v = int (v)
                attr.__set__ (entity, v)
        elif session.scope.reserve_surrogates :
            self.reserve (session, v)
        if v is not None :
            akw = self.ETW.db_attrs [attr.name]
            kw [akw.ckd_name] = v
    # end def insert

    def max_value (self, session) :
        conn = self.connection (session)
        return conn.execute (self.select).scalar () or 0
    # end def max_value

    def reserve (self, session, value, commit = True, force = False) :
        conn      = self.connection (session)
        max_value = self.max_value  (session)
        ### `undo` of changes comes here with existing values, ignore those
        if force or value > max_value :
            self._reserve (conn, value)
            session.seq_high [self] = value
            if commit :
                session.con_man_seq.commit ()
        return value
    # end def reserve

    def rollback (self, session) :
        pass
    # end def rollback

    def _reserve (self, conn, value) :
        pass
    # end def _reserve

    def __repr__ (self) :
        attr = self.attr
        return "<Sequence for %s attribute %s.%s>" % \
            (attr.typ, self.type_name, attr.name)
    # end def __repr__

# end class _Sequence_

class _Sequence_S_ (_Sequence_) :
    """Wrap a database sequence for a RDBMS supporting sequences"""

    _seq_kw             = {}

    def __init__ (self, attr, ETW, ** kw) :
        self._seq_kw = dict (self._seq_kw, ** kw) ### merge _seq_kw of class, kw
        self.__super.__init__ (attr, ETW)
    # end def __init__

    @TFL.Meta.Once_Property
    def sa_seq (self) :
        return SA.schema.Sequence (self.seq_name, ** self._seq_kw)
    # end def sa_seq

    @TFL.Meta.Once_Property
    def col_args (self) :
        return (self.sa_seq, )
    # end def col_args

# end class _SAW_Sequence_S_

class Sequence (_Sequence_) :
    """Wrap or emulate a database sequence without its own sequence table"""

    @TFL.Meta.Once_Property
    def select (self) :
        col = self.ETW.spk_col
        return SA.sql.select ([col]).order_by (col.desc ()).limit (1)
    # end def select

    @TFL.Meta.Once_Property
    def sa_table (self) :
        return self.ETW.sa_table
    # end def sa_table

    @TFL.Meta.Once_Property
    def table_name (self) :
        return self.ETW.table_name
    # end def table_name

    def connection (self, session) :
        return session.con_man.connection
    # end def connection

    def extract (self, session, entity, kw, sa_result) :
        attr   = self.attr
        result = int (sa_result.inserted_primary_key [0])
        akw    = self.ETW.db_attrs [attr.name]
        attr.__set__ (entity, result)
        kw [akw.ckd_name] = result
        return result
    # end def extract

    def next_value (self, session, commit = True) :
        pass
    # end def next_value

# end class Sequence

class Sequence_PID (Sequence) :
    """Wrap or emulate a database sequence for `pid`"""

    @TFL.Meta.Once_Property
    def select_md_change (self) :
        ETW = self.ATW ["MOM.MD_Change"]
        col = ETW.QC   ["pid"]
        return SA.sql.select ([col]).order_by (col.desc ()).limit (1)
    # end def select_md_change

    def max_value (self, session) :
        conn = session.con_man.connection
        return max \
            ( conn.execute (self.select).scalar () or 0
            , conn.execute (self.select_md_change).scalar () or 0
            )
    # end def max_value

# end class Sequence_PID

class Sequence_X (_Sequence_) :
    """Wrap or emulate a database sequence with its own sequence table"""

    def __init__ (self, attr, ETW) :
        self.__super.__init__ (attr, ETW)
        self.table_name = tn  = "%s_table"  % (self.seq_name, )
        self.sa_column  = col = self._define_column (attr, self.DBW)
        self.sa_table   = tab = self._define_table  (tn,   self.DBW, col)
        self.del_stmt   = tab.delete ().where (col < SA.sql.bindparam ("max"))
        self.ins_stmt   = tab.insert ()
        self.select     = SA.sql.select ([col]).limit (1).order_by (col.desc ())
    # end def __init__

    def close (self, session) :
        self.rollback (session)
    # end def close

    def commit (self, session) :
        session.con_man_seq.commit ()
    # end def commit

    def connection (self, session) :
        return session.con_man_seq.connection
    # end def connection

    def next_value (self, session, commit = True) :
        con_man = session.con_man_seq
        conn    = con_man.connection
        sar     = conn.execute (self.ins_stmt.values ())
        result  = session.seq_high [self] = int (sar.inserted_primary_key [0])
        conn.execute (self.del_stmt, max = result)
        if commit :
            con_man.commit ()
        return result
    # end def next_value

    def rollback (self, session) :
        session.con_man_seq.rollback ()
    # end def rollback

    def _define_column (self, attr, DBW, * args, ** kw) :
        return SA.schema.Column \
            ( attr.name
            , self.ATW.SA_Type.sized_int_type (attr.Pickled_Type)
            , * (self.col_args + args)
            , ** dict (self._column_kw, primary_key = True, ** kw)
            )
    # end def _define_column

    def _define_table (self, tn, DBW, * cols, ** kw) :
        return SA.schema.Table \
            ( tn, self.ATW.metadata, * cols
            , ** dict (self._table_kw, ** kw)
            )
    # end def _define_table

    def _reserve (self, conn, value) :
        conn.execute (self.ins_stmt.values (** {self.attr.name : value}))
        conn.execute (self.del_stmt, max = value)
    # end def _reserve

# end class Sequence_X

MOM.Attr.A_Surrogate._saw_sequence_type_name                 = "Sequence_X"
MOM.Id_Entity.E_Spec._Attributes.pid._saw_sequence_type_name = "Sequence_PID"
MOM.MD_Change.E_Spec._Attributes.cid._saw_sequence_type_name = "Sequence"

@TFL.Add_To_Class ("_saw_sequence", MOM.Attr.A_Surrogate)
def _saw_sequence (self, ETW) :
    ST = getattr (ETW.PNS, self._saw_sequence_type_name)
    return ST (self.kind, ETW)
# end def _saw_sequence

if __name__ != "__main__" :
    MOM.DBW.SAW._Export ("*", "_Sequence_", "_Sequence_S_")
### __END__ MOM.DBW.SAW.Sequence
