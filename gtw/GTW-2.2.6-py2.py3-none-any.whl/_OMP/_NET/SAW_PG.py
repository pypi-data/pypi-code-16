# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.NET.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.NET.SAW_PG
#
# Purpose
#    SAW specific functions and classes for GTW.OMP.NET attribute types
#
# Revision Dates
#     2-Aug-2013 (CT) Creation
#     6-Aug-2013 (CT) Finish creation
#    20-Sep-2013 (CT) Add `QX`, remove `_q_exp_call_apply` method
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                       import GTW
from   _MOM                       import MOM
from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

import _GTW._OMP._NET.Attr_Type
import _GTW._OMP._NET.SAW

from   _MOM._DBW._SAW             import QX, SAW, SA
from   _MOM.SQ                    import Q

import _MOM._DBW._SAW.Attr
import _MOM._DBW._SAW._PG.Attr
import _MOM._DBW._SAW._PG.SA_Type

from   _TFL._Meta.Single_Dispatch import Single_Dispatch_Method

import _TFL._Meta.Object
import _TFL.Decorator

class _CIDR_Type_ (GTW.OMP.NET.SAW._CIDR_Type_) :
    """Augmented CIDR type that converts between R_IP_Address and
       PostgreSQL CIDR.
    """

    impl = SAW.PG.SA_Type.CIDR

# end class _CIDR_Type_

class Kind_Wrapper_CIDR \
          (SAW.Attr._Kind_Wrapper_Field_Extractor_, SAW.Attr.Kind_Wrapper) :

    fields = set (("mask_len", ))
    op_map = dict \
        ( contains = ">>="
        , in_      = "<<="
        )

# end class Kind_Wrapper_CIDR

class _QX_Call_Proxy_ (TFL.Meta.Object) :
    """Proxy for a CIDR method call"""

    def __init__ (self, qx, akw, name, op_name) :
        self.qx      = qx
        self.akw     = akw
        self.name    = name
        self.op_name = op_name
    # end def __init__

    def __call__ (self, lhs, rhs) :
        ### `lhs` should be a SQLAlchemy column object
        ###    `lhs.op` returns a generic operator function
        op = lhs.op (self.op_name)
        return op (rhs)
    # end def __call__

# end class _QX_Call_Proxy_

@TFL.Add_To_Class ("QX", Kind_Wrapper_CIDR)
class _QX_CIDR_ (QX.Kind) :
    """QX mapper base class for CIDR attributes"""

    def _op_call (self, name, op, * args, ** kw) :
        akw = self._akw
        if self._field or name not in akw.op_map :
            return self.__super._op_call (name, op, * args, ** kw)
        else :
            op_name  = akw.op_map [name]
            op_proxy = _QX_Call_Proxy_ (self, akw, name, op_name)
            return QX.Call (self, name, op_proxy, * args, ** kw)
    # end def _op_call

# end class _QX_CIDR_

PG_Man_Class = SAW.PG.Manager.__class__

@GTW.OMP.NET._A_CIDR_._saw_column_type.add_type (PG_Man_Class)
def _saw_column_type_CIDR_PG (self, DBW, wrapper, pts) :
    return _CIDR_Type_ ()
# end def _saw_column_type_CIDR_PG

@GTW.OMP.NET._A_CIDR_._saw_extract_field.add_type (PG_Man_Class)
def _saw_extract_field_mask_CIDR_PG (self, DBW, col, field) :
    if field == "mask_len" :
        return SA.func.masklen (col)
    raise AttributeError (field)
# end def _saw_extract_field_mask_CIDR_PG

@GTW.OMP.NET._A_CIDR_._saw_kind_wrapper.add_type (PG_Man_Class)
def _saw_kind_wrapper_CIDR_PG (self, DBW, ETW, kind, ** kw) :
    return Kind_Wrapper_CIDR (ETW, kind, ** kw)
# end def _saw_kind_wrapper_CIDR_PG

if __name__ != "__main__" :
    GTW.OMP.NET._Export_Module ()
### __END__ GTW.OMP.NET.SAW_PG
