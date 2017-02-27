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
#    MOM.DBW.SAW.PG.Manager
#
# Purpose
#    Database wrapper for PostgreSQL accessed by sqlalchemy wrapped by SAW
#
# Revision Dates
#    21-Jun-2013 (CT) Creation
#    28-Jul-2013 (CT) Add import for `...PG.Sequence`
#     2-Aug-2013 (CT) Add import for `...PG.SA_Type`
#    10-Aug-2016 (CT) Add `ExcludeConstraint` to `_add_check_constraints`
#    ««revision-date»»···
#--

from   __future__                 import division, print_function
from   __future__                 import absolute_import, unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL

from   _TFL.pyk                   import pyk

from   _MOM._DBW._SAW             import SA

from sqlalchemy.dialects.postgresql import ExcludeConstraint

import _MOM._DBW._SAW.Manager
class _M_SAW_PG_Manager_ (MOM.DBW.SAW.Manager.__class__) :
    """Meta class of MOM.DBW.SAW.PG.Manager"""

    def _add_check_constraints (cls, e_type, ETW, sa_table) :
        cls.__m_super._add_check_constraints (e_type, ETW, sa_table)
        own_names = e_type._Predicates._own_names
        QR        = ETW.Q_Result
        QX        = QR.QX
        for pk in e_type.P_exclusion :
            if pk.name in own_names :
                pred    = pk.pred
                columns = []
                tables  = set ((sa_table, ))
                for qs in pred.aqs :
                    qx  = QX.Mapper (QR) (qs)
                    op  = qx.exclude_constraint_op
                    columns.extend ((c, op) for c in qx.XS_ATTR)
                    for join in qx.JOINS :
                        tables.update (j.table for j in join)
                if len (tables) == 1 :
                    if pk.auto_index :
                        for c, op in columns :
                            idx_name = "__".join ([sa_table.name, c.name, "gist"])
                            SA.schema.Index (idx_name, c, postgresql_using='gist')
                    c_name  = "__".join ([sa_table.name, pk.name])
                    exclude = ExcludeConstraint (* columns, name = c_name)
                    sa_table.append_constraint (exclude)
                    pred.ems_check = False
    # end def _add_check_constraints

# end class _M_SAW_PG_Manager_

class _SAW_PG_Manager_ \
          (TFL.Meta.BaM (MOM.DBW.SAW.Manager, metaclass = _M_SAW_PG_Manager_)) :
    """Database wrapper for SAW-wrapped sqlalchemy-PostgreSQL"""

    _real_name    = "Manager"

    PNS           = MOM.DBW.SAW.PG

Manager = _SAW_PG_Manager_ # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.PG._Export ("*")

    ### The following modules dispatch on `Manager.__class__` and therefore
    ### needs to import `Manager`. Due to the cycle we need to import them
    ### after defining and exporting `Manager`
    import _MOM._DBW._SAW._PG.Attr
    import _MOM._DBW._SAW._PG.DBS
    import _MOM._DBW._SAW._PG.E_Type_Wrapper
    import _MOM._DBW._SAW._PG.Pid_Manager
    import _MOM._DBW._SAW._PG.SA_Type
    import _MOM._DBW._SAW._PG.Sequence
### __END__ MOM.DBW.SAW.PG.Manager
