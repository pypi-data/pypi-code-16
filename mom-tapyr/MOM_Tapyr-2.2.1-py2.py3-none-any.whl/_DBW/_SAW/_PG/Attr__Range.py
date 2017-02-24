# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
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
#    MOM.DBW.SAW.PG.Attr__Range
#
# Purpose
#    Range-attribute handling for SAW.PG
#
# Revision Dates
#    29-Jul-2016 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _MOM._DBW._SAW             import QX, SAW, SA

import _MOM._Attr.Range
import _MOM._Attr.Range_DT
import _MOM._DBW._SAW.QX
import _MOM._DBW._SAW._PG.SA_Type

from   _TFL._Meta.Single_Dispatch import Single_Dispatch_Method

import _TFL._Meta.Object
import _TFL.Decorator

import datetime
import operator
import psycopg2.extras
import sqlalchemy.dialects.postgresql.ranges as pg_ranges

class _SA_Type_Range_ (SA.types.TypeDecorator) :
    """Augmented range type that converts TFL.Range instances to/from
       PostgreSQL.
    """

    _convert_stype_pg2py = None
    _convert_stype_py2pg = None

    def __init__ (self, P_Type, btype, * args, ** kw) :
        self.P_Type = P_Type
        self.btype  = btype
    # end def __init__

    def process_bind_param   (self, value, dialect) :
        PT      = self.P_Type
        ST      = PT.S_Type
        convert = self._convert_stype_py2pg
        if value is None :
            result  = value
        elif isinstance (value, ST) :
            result  = value if convert is None else convert (value)
        else :
            if isinstance (value, PT) :
                bounds  = value.lower, value.upper
            elif isinstance (value, tuple) :
                bounds  = tuple (v [0] for v in value)
            else :
                return value
            if convert is not None :
                bounds  = tuple (convert (x) for x in bounds)
            result  = self.PG_Type (* bounds, bounds = self.btype)
        return result
    # end def process_bind_param

    def process_result_value (self, value, dialect) :
        if isinstance (value, psycopg2.extras.Range) :
            convert = self._convert_stype_pg2py
            bounds  = value.lower, value.upper
            if convert is not None :
                bounds = tuple (convert (x) for x in bounds)
            result = tuple ((x, ) for x in bounds)
        else :
            result = value
        return result
    # end def process_result_value

# end class _SA_Type_Range_

@TFL.Add_New_Method (MOM.DBW.SAW.PG.SA_Type)
class Date_Range (_SA_Type_Range_) :
    """Augmented date range type."""

    impl    = pg_ranges.DATERANGE
    PG_Type = psycopg2.extras.DateRange

# end class Date_Range

@TFL.Add_New_Method (MOM.DBW.SAW.PG.SA_Type)
class Date_Time_Range (_SA_Type_Range_) :
    """Augmented date-time range type."""

    impl    = pg_ranges.TSRANGE ()
    PG_Type = psycopg2.extras.DateTimeRange

# end class Date_Time_Range

@TFL.Add_New_Method (MOM.DBW.SAW.PG.SA_Type)
class Int_Range (_SA_Type_Range_) :
    """Augmented integer range type."""

    impl    = pg_ranges.NUMRANGE
    PG_Type = psycopg2.extras.NumericRange

# end class Int_Range

@TFL.Add_New_Method (MOM.DBW.SAW.PG.SA_Type)
class Time_Range (Date_Time_Range) :
    """Augmented time range type."""

    _fake_date = datetime.date (1, 1, 1)

    def _convert_stype_pg2py (self, value) :
        if isinstance (value, datetime.datetime) :
            value = value.time ()
        return value
    # end def _convert_stype_pg2py

    def _convert_stype_py2pg (self, value) :
        if isinstance (value, datetime.time) :
            value = datetime.datetime.combine (self._fake_date, value)
        return value
    # end def _convert_stype_py2pg

# end class Time_Range

class Kind_Wrapper_Range (SAW.Attr.Kind_Wrapper_Structured_Field_Extractor) :
    """SAW.PG specific information about an range-attribute kind
       descriptor in the context of a specific E_Type_Wrapper
    """

    fields = set (("lower", "upper"))
    op_map = dict \
        ( contains = "@>"
        , overlaps = "&&"
        , in_      = "<@"
        )

# end class Kind_Wrapper_Range

class _QX_Call_Proxy_ (TFL.Meta.Object) :
    """Proxy for a CIDR method call"""

    def __init__ (self, qx, akw, name, op_name) :
        self.qx      = qx
        self.akw     = akw
        self.name    = name
        self.op_name = op_name
    # end def __init__

    def __call__ (self, lhs, rhs) :
        op  = lhs.op (self.op_name)
        qx  = self.qx
        rhs = qx._xs_filter_rhs (rhs)
        if isinstance (rhs, QX._Base_) :
            rhs = qx._xs_filter_rhs (rhs)
        return op (rhs)
    # end def __call__

# end class _QX_Call_Proxy_

@TFL.Add_To_Class ("QX", Kind_Wrapper_Range)
class _QX_Range_ (QX.Kind_Structured_Field_Extractor) :
    """QX mapper class for Range attributes"""

    exclude_constraint_op = "&&"

    def _op_call (self, name, op, * args, ** kw) :
        akw = self._akw
        if self._field or name not in akw.op_map :
            return self.__super._op_call (name, op, * args, ** kw)
        else :
            op_name   = akw.op_map [name]
            op_proxy  = _QX_Call_Proxy_ (self, akw, name, op_name)
            return QX.Call (self, name, op_proxy, * args, ** kw)
    # end def _op_call

# end class _QX_Range_

@TFL.Add_To_Class ("_saw_column_type", MOM.Attr._A_Range_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_range (self, DBW, wrapper, pts) :
    PT = self.P_Type
    RT = getattr (wrapper.ATW.SA_Type, PT.__name__)
    return RT (PT, self.default_btype)
# end def _saw_column_type_range

PG_Man_Class = SAW.PG.Manager.__class__

@MOM.Attr._A_Range_._saw_bool.add_type (PG_Man_Class)
def _saw_bool_range_PG (self, DBW, col) :
    NOT = SA.sql.not_
    return NOT (SA.func.isempty (col))
# end def _saw_bool_range_PG

@MOM.Attr._A_Range_._saw_extract_field.add_type (PG_Man_Class)
def _saw_extract_field_mask_Range_PG (self, DBW, col, field) :
    if field == "lower" :
        result = SA.func.lower (col)
    elif field == "upper" :
        result = SA.func.upper (col)
    elif field == "btype" :
        lb = SA.expression.cast (SA.func.lower_inc (col), SA.types.Integer)
        ub = SA.expression.cast (SA.func.upper_inc (col), SA.types.Integer)
        result = SA.func.concat \
            (SA.func.substr ("([", lb, 1), SA.func.substr (")]", ub, 1))
    else :
        raise AttributeError (field)
    return result
# end def _saw_extract_field_mask_Range_PG

@MOM.Attr._A_Range_._saw_kind_wrapper.add_type (PG_Man_Class)
def _saw_kind_wrapper_Range_PG (self, DBW, ETW, kind, ** kw) :
    return Kind_Wrapper_Range (ETW, kind, ** kw)
# end def _saw_kind_wrapper_Range_PG

if __name__ != "__main__" :
    MOM.DBW.SAW.PG._Export_Module ()
### __END__ MOM.DBW.SAW.PG.Attr__Range
