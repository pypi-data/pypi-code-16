# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.Attr_Range
#
# Purpose
#    Test MOM.Attr.Range types
#
# Revision Dates
#    20-Jul-2016 (CT) Creation
#     7-Sep-2016 (CT) Add `_test_structured`
#     9-Sep-2016 (CT) Add `_test_MF3`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                              import GTW

import _GTW._OMP._PAP.import_PAP
from   _GTW.__test__.model               import *
from   _GTW.__test__._SAW_test_functions import *
from   _GTW.__test__.MF3                 import \
    show_elements, show_elements_x, show_completers

from   _MOM.import_MOM                   import *
from   _MOM._Attr.Range_DT               import *

import datetime

from   _TFL.Regexp                       import Regexp, Re_Replacer, re

_cleaner = Re_Replacer \
    ( Regexp
        ( r"'sigs' : [^{]*\{[^}]*\}"
        , re.MULTILINE
        )
    , r"'sigs' : { ... }"
    )

def show_formatted (x) :
    result = _cleaner (formatted (x))
    print (result)
# end def show_formatted

_Ancestor_Essence = GTW.OMP.PAP.Link1

class Appointment (_Ancestor_Essence) :
    """Personal appointment to test range types"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :

            role_type          = GTW.OMP.PAP.Person

        # end class left

        class date (A_Date) :
            """Date of appointment."""

            kind               = Attr.Primary
            completer          = Attr.Completer_Spec  (4, Attr.Selector.primary)

        # end class date

        class time (A_Time_Range) :
            """Time range of appointment."""

            kind               = Attr.Primary
            completer          = Attr.S_Completer_Spec  (2, Attr.Selector.primary)

        # end class time

        ### Non-primary attributes

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        _Ancestor = _Ancestor_Essence._Predicates

        exclusive_left_date_time = Pred.Exclude.New_Pred \
            ( "left", "date", "time"
            , name           = "exclusive_left_date_time"
            , exclude_op_map = dict
                ( time       = "OVERLAPS"
                )
            )

    # end class _Predicates

# end class Appointment

_test_attr_wrappers_pg = r"""
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_attr_wrappers (apt, lambda x : x.e_type.type_base_name == "Appointment")
    PAP.Appointment
      Kind_Wrapper_Date : Date `date`
          _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
        <SAW : Date `date` [pap_appointment.date
          Kind_Wrapper_Q : Int `day`
              Query, _Cached_, _Volatile_, _System_
          Kind_Wrapper_Q : Int `month`
              Query, _Cached_, _Volatile_, _System_
          Kind_Wrapper_Q : Int `year`
              Query, _Cached_, _Volatile_, _System_
      Kind_Wrapper_S : Person `left`
          Init_Only_Mixin, _Just_Once_Mixin_, Link_Role, _EPK_Mixin_, _SPK_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
      Kind_Wrapper_Range : Time_Range `time`
          _Range_Mixin_, _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
        <SAW : Time_Range `time` [pap_appointmen
          Kind_Wrapper_Time : Time `lower`
              _Structured_Mixin_, Optional, _User_, _DB_Attr_
          <SAW : Time `time.lower` [time__lower]>
             Kind_Wrapper_Q : Int `hour`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `minute`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `second`
                 Query, _Cached_, _Volatile_, _System_
          Kind_Wrapper_Time : Time `upper`
              _Structured_Mixin_, Optional, _User_, _DB_Attr_
          <SAW : Time `time.upper` [time__upper]>
             Kind_Wrapper_Q : Int `hour`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `minute`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `second`
                 Query, _Cached_, _Volatile_, _System_

    >>> show_attr_mro (apt ["PAP.Appointment"])
    PAP.Appointment
      creation             -> MOM.MD_Change
        Computed, _Rev_Query_, _Cached_, _Volatile_, _System_
      date
        _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
      events               -> EVT.Event
        Computed, _Rev_Query_, _Cached_, _Volatile_, _System_
      last_change          -> MOM.MD_Change
        Computed, _Rev_Query_, _Cached_, _Volatile_, _System_
      last_cid
        Internal, _DB_System_, _DB_Attr_, _System_
      left                 -> PAP.Person
        Init_Only_Mixin, _Just_Once_Mixin_, Link_Role, _EPK_Mixin_, _SPK_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
      pid
        Just_Once_Mixin, _Just_Once_Mixin_, Internal, _DB_System_, _DB_Attr_, _System_
      time
        _Range_Mixin_, _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
        lower
          _Structured_Mixin_, Optional, _User_, _DB_Attr_
        upper
          _Structured_Mixin_, Optional, _User_, _DB_Attr_
      type_name
        _Type_Name_Mixin_, Internal, _DB_System_, _DB_Attr_, _System_

"""

_test_attr_wrappers_sq = r"""
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_attr_wrappers (apt, lambda x : x.e_type.type_base_name == "Appointment")
    PAP.Appointment
      Kind_Wrapper_Date : Date `date`
          _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
        <SAW : Date `date` [pap_appointment.date
          Kind_Wrapper_Q : Int `day`
              Query, _Cached_, _Volatile_, _System_
          Kind_Wrapper_Q : Int `month`
              Query, _Cached_, _Volatile_, _System_
          Kind_Wrapper_Q : Int `year`
              Query, _Cached_, _Volatile_, _System_
       Kind_Wrapper_S : Person `left`
          Init_Only_Mixin, _Just_Once_Mixin_, Link_Role, _EPK_Mixin_, _SPK_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
      Kind_Wrapper_Range : Time_Range `time`
          _Range_Mixin_, _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
        time__445__type_desc
          Kind_Wrapper_Time : Time `lower`
              _Structured_Mixin_, Optional, _User_, _DB_Attr_
          <SAW : Time `time.lower` [pap_appointmen
             Kind_Wrapper_Q : Int `hour`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `minute`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `second`
                 Query, _Cached_, _Volatile_, _System_
          Kind_Wrapper_Time : Time `upper`
              _Structured_Mixin_, Optional, _User_, _DB_Attr_
          <SAW : Time `time.upper` [pap_appointmen
             Kind_Wrapper_Q : Int `hour`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `minute`
                 Query, _Cached_, _Volatile_, _System_
             Kind_Wrapper_Q : Int `second`
                 Query, _Cached_, _Volatile_, _System_

    >>> show_attr_mro (apt ["PAP.Appointment"])
    PAP.Appointment
      creation             -> MOM.MD_Change
        Computed, _Rev_Query_, _Cached_, _Volatile_, _System_
      date
        _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
      events               -> EVT.Event
        Computed, _Rev_Query_, _Cached_, _Volatile_, _System_
      last_change          -> MOM.MD_Change
        Computed, _Rev_Query_, _Cached_, _Volatile_, _System_
      last_cid
        Internal, _DB_System_, _DB_Attr_, _System_
      left                 -> PAP.Person
        Init_Only_Mixin, _Just_Once_Mixin_, Link_Role, _EPK_Mixin_, _SPK_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
      pid
        Just_Once_Mixin, _Just_Once_Mixin_, Internal, _DB_System_, _DB_Attr_, _System_
      time
        _Range_Mixin_, _Structured_Mixin_, Primary, _Required_Mixin_, _Primary_, _User_, _DB_Attr_
        lower
          _Structured_Mixin_, Optional, _User_, _DB_Attr_
        upper
          _Structured_Mixin_, Optional, _User_, _DB_Attr_
      type_name
        _Type_Name_Mixin_, Internal, _DB_System_, _DB_Attr_, _System_

"""

_test_main = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP   = scope.PAP
    >>> dtt   = datetime.time
    >>> tak   = PAP.Appointment.E_Type.time
    >>> inf   = tak.P_Type (None, None)

    >>> p = PAP.Person.instance_or_new ("Tanzer", "Christian", raw = True)
    >>> p
    PAP.Person ('tanzer', 'christian', '', '')

    >>> a = PAP.Appointment (p, "2016-07-20", "[14, 16)", raw = True)
    >>> b = PAP.Appointment (p, "2016-07-21", "[08:30, 09:00)", raw = True)
    >>> print (a.ui_display) # before commit
    Tanzer Christian, 2016-07-20, [14:00, 16:00)
    >>> print (b.ui_display) # before commit
    Tanzer Christian, 2016-07-21, [08:30, 09:00)

    >>> print (portable_repr (tak.get_pickle_cargo (a))) # before commit
    (((datetime.time(14, 0),), (datetime.time(16, 0),)),)

    >>> scope.commit ()
    >>> print (a.ui_display) # after commit
    Tanzer Christian, 2016-07-20, [14:00, 16:00)

    >>> print (b.ui_display) # after commit
    Tanzer Christian, 2016-07-21, [08:30, 09:00)

    >>> PAP.Appointment.query (Q.time == Q.time).order_by (Q.time).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)')), PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time == a.time).order_by (Q.time).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time <  a.time).order_by (Q.time).attr (Q.time).all ()
    [Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)')]

    >>> PAP.Appointment.query (Q.time <= a.time).order_by (Q.time).attr (Q.time).all ()
    [Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'), Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)')]

    >>> PAP.Appointment.query (Q.time >= a.time).order_by (Q.time).attr (Q.time).all ()
    [Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)')]

    >>> PAP.Appointment.query (Q.time >  a.time).order_by (Q.time).attr (Q.time).all ()
    []

    >>> PAP.Appointment.query (Q.time != Q.time).all ()
    []

    >>> PAP.Appointment.query (Q.time != a.time).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time.lower == Q.time.upper).order_by (Q.time).all ()
    []

    >>> PAP.Appointment.query (Q.time.lower <= Q.time.upper).order_by (Q.time).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)')), PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time.lower.minute >= 30).order_by (Q.time).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time.lower.minute < 30).order_by (Q.time).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time.CONTAINS (dtt (8, 45))).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time.CONTAINS (dtt (8, 45))).attr (Q.time).all ()
    [Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)')]

    >>> PAP.Appointment.query (Q.time.IN (tak.from_string ("08:00, 12:00"))).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> PAP.Appointment.query (Q.time.IN (tak.from_string ("09:00, 12:00"))).all ()
    []

    >>> PAP.Appointment.query (Q.time.IN (inf)).order_by (Q.date, Q.time).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)')), PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> tak.from_string ("08:45, 09:00")
    Time_Range (datetime.time(8, 45), datetime.time(9, 0), '[)')

    >>> PAP.Appointment.query (Q.time.CONTAINS (tak.from_string ("08:45, 09:00"))).attr (Q.time).all ()
    [Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)')]

    >>> PAP.Appointment.query (Q.time.CONTAINS (tak.from_string ("08:45, 09:01"))).attr (Q.time).all ()
    []

    >>> PAP.Appointment.query (Q.time.CONTAINS (dtt (8, 45))).attr (Q.time.lower).all ()
    [datetime.time(8, 30)]

    >>> PAP.Appointment.query (Q.time.OVERLAPS (tak.from_string ("13, 15"))).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))]

    >>> l = tak.attr.E_Type.lower
    >>> l, l.attr.ckd_name
    (Time `lower`, 'lower')

    >>> tak.attr.E_Type.db_attr
    [Time `lower`, Time `upper`]

    >>> pc = tak.get_pickle_cargo (a)
    >>> print (portable_repr (pc))
    (((datetime.time(14, 0),), (datetime.time(16, 0),)),)

    >>> tr = tak.from_pickle_cargo (scope, pc)
    >>> tr == a.time
    True
    >>> tr == tak.from_pickle_cargo (scope, (a.time, ))
    True
    >>> print (tr)
    [14:00, 16:00)

    >>> PAP.Appointment.E_Type.P_uniqueness
    [Uniqueness predicate: unique_epk ('left', 'date', 'time')]

    >>> PAP.Appointment.E_Type.P_exclusion
    [Exclusion predicate: exclusive_left_date_time ('left', 'date', 'time')]

    >>> with expect_except (MOM.Error.Invariants) :
    ...     c = PAP.Appointment (p, "2016-07-21", "[08:00, 09:00)", raw = True)
    Invariants: The attribute values for ('left', 'date', 'time') must be exclusive for each object
      The new definition of Appointment PAP.Appointment (('Tanzer', 'Christian', '', '', 'PAP.Person'), '2016-07-21', '[08:00, 09:00)') would clash with 1 existing entities
      Already existing:
        PAP.Appointment (('Tanzer', 'Christian', '', '', 'PAP.Person'), '2016-07-21', '[08:30, 09:00)')

    >>> scope.rollback ()

    >>> PAP.Appointment.query (Q.time.lower == dtt (8, 30)).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> PAP.Appointment.query (PAP.Appointment.AQ.time.lower.AC ("8:30")).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> PAP.Appointment.query (PAP.Appointment.AQ.time.lower.AC ("8")).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]

    >>> PAP.Appointment.query (PAP.Appointment.AQ.time.upper.AC ("16")).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))]

    >>> PAP.Appointment.query (PAP.Appointment.AQ.time.lower.AC (":0")).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))]

    >>> PAP.Appointment.query (PAP.Appointment.AQ.time.lower.AC (":30")).all ()
    [PAP.Appointment (('tanzer', 'christian', '', ''), '2016-07-21', Time_Range (datetime.time(8, 30), datetime.time(9, 0), '[)'))]


"""

_test_MF3 = r"""
    >>> from _GTW._MF3 import Element as MF3_E
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP   = scope.PAP

    >>> p     = PAP.Person.instance_or_new ("Tanzer", "Christian", raw = True)
    >>> a     = PAP.Appointment (p, "2016-07-20", "[14, 16)", raw = True)

    >>> F_A   = MF3_E.Entity.Auto (PAP.Appointment, id_prefix = "A")
    >>> F_A_s = MF3_E.Entity.Auto (PAP.Appointment, id_prefix = "A", attr_spec = { "time.upper" : dict (skip = True)})
    >>> f_a   = F_A (scope, a)

    >>> show_elements (F_A, "q_name")
    <class Entity A-114> None
    <class Field_Entity A-114:left> left
    <class Field A-114:left.last_name> left.last_name
    <class Field A-114:left.first_name> left.first_name
    <class Field A-114:left.middle_name> left.middle_name
    <class Field A-114:left.title> left.title
    <class Field A-114:date> date
    <class Field_Structured A-114:time> time
    <class Field A-114:time.lower> time.lower
    <class Field A-114:time.upper> time.upper

    >>> show_elements (F_A_s, "q_name")
    <class Entity A-114> None
    <class Field_Entity A-114:left> left
    <class Field A-114:left.last_name> left.last_name
    <class Field A-114:left.first_name> left.first_name
    <class Field A-114:left.middle_name> left.middle_name
    <class Field A-114:left.title> left.title
    <class Field A-114:date> date
    <class Field_Structured A-114:time> time
    <class Field A-114:time.lower> time.lower

    >>> show_elements (f_a, "edit")
    <Entity A-114> ---
    <Field_Entity A-114:left> 1
    <Field A-114:date> 2016-07-20
    <Field_Structured A-114:time>
    <Field A-114:time.lower> 14:00
    <Field A-114:time.upper> 16:00

    >>> show_elements (f_a, "ui_display")
    <Entity A-114> Tanzer Christian, 2016-07-20, [14:00, 16:00)
    <Field_Entity A-114:left> Tanzer Christian
    <Field A-114:date> 2016-07-20
    <Field_Structured A-114:time> [14:00, 16:00)
    <Field A-114:time.lower> 14:00
    <Field A-114:time.upper> 16:00

    >>> show_elements (f_a, "essence")
    <Entity A-114> (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))
    <Field_Entity A-114:left> ('tanzer', 'christian', '', '')
    <Field A-114:date> (('tanzer', 'christian', '', ''), '2016-07-20', Time_Range (datetime.time(14, 0), datetime.time(16, 0), '[)'))
    <Field_Structured A-114:time> [14:00, 16:00)
    <Field A-114:time.lower> [14:00, 16:00)
    <Field A-114:time.upper> [14:00, 16:00)

    >>> show_elements (f_a, "Entity")
    <Entity A-114> <Entity A-114>
    <Field_Entity A-114:left> <Entity A-114>
    <Field A-114:date> <Entity A-114>
    <Field_Structured A-114:time> <Entity A-114>
    <Field A-114:time.lower> <Entity A-114>
    <Field A-114:time.upper> <Entity A-114>

    >>> show_elements (f_a, "template_macro")
    <Entity A-114> Entity_Form
    <Field_Entity A-114:left> Field_Entity
    <Field A-114:date> Field
    <Field_Structured A-114:time> Field_Structured
    <Field A-114:time.lower> Field
    <Field A-114:time.upper> Field

    >>> show_elements (f_a, "template_module")
    <Entity A-114> mf3
    <Field_Entity A-114:left> None
    <Field A-114:date> None
    <Field_Structured A-114:time> mf3_h_cols
    <Field A-114:time.lower> None
    <Field A-114:time.upper> None

    >>> show_elements (f_a, "label")
    <Entity A-114> Appointment
    <Field_Entity A-114:left> Person
    <Field A-114:date> Date
    <Field_Structured A-114:time> Time
    <Field A-114:time.lower> start
    <Field A-114:time.upper> finish

    >>> show_elements (f_a, "completer")
    <Entity A-114> None
    <Field_Entity A-114:left> None
    <Field A-114:date> <Completer for <Field A-114:date>, treshold = 4, entity_p = 1>
    <Field_Structured A-114:time> <C_Completer for <Field_Structured A-114:time>, treshold = 2, entity_p = 1>
    <Field A-114:time.lower> <Completer for <Field A-114:time.lower>, treshold = 2, entity_p = 0>
    <Field A-114:time.upper> <Completer for <Field A-114:time.upper>, treshold = 2, entity_p = 0>

    >>> show_completers (f_a, "q_name", "attr.completer.kind")
    Type    q_name      attr.completer.kind
    ================================
    F       date        Atom
    F_S     time        Structured
    F       time.lower  Atom
    F       time.upper  Atom

    >>> show_completers (f_a, "q_name", "completer.elems")
    Type    q_name      completer.elems
    =========================================================================================================================
    F       date        (<Field A-114:date>, <Field_Entity A-114:left>, <Field A-114:time.lower>, <Field A-114:time.upper>)
    F_S     time        (<Field A-114:time.lower>, <Field A-114:time.upper>, <Field A-114:date>)
    F       time.lower  (<Field A-114:time.lower>,)
    F       time.upper  (<Field A-114:time.upper>,)

    >>> show_completers (f_a, "q_name", "completer.etn", "completer.attr_names")
    Type    q_name      completer.etn    completer.attr_names
    ===================================================================================
    F       date        PAP.Appointment  ('date', 'left', 'time.lower', 'time.upper')
    F_S     time        PAP.Appointment  ('time.lower', 'time.upper', 'date')
    F       time.lower  PAP.Appointment  ('time.lower',)
    F       time.upper  PAP.Appointment  ('time.upper',)

    >>> show_formatted (f_a.as_json_cargo)
    { 'buddies' :
        { 1 :
            [ 'A-114:date'
            , 'A-114:left'
            , 'A-114:time.lower'
            , 'A-114:time.upper'
            ]
        , 2 : ['A-114:time.lower']
        , 3 : ['A-114:time.upper']
        }
    , 'cargo' :
        { 'field_values' :
            { 'A-114:date' : {'init' : '2016-07-20'}
            , 'A-114:left' :
                { 'init' :
                    { 'cid' : 1
                    , 'display' : 'Tanzer Christian'
                    , 'pid' : 1
                    }
                }
            , 'A-114:time.lower' : {'init' : '14:00'}
            , 'A-114:time.upper' : {'init' : '16:00'}
            }
        , 'pid' : 2
        , 'sid' : 0
        , 'sigs' : { ... }
        }
    , 'checkers' : {}
    , 'completers' :
        { 1 :
            { 'buddies_id' : 1
            , 'entity_p' : True
            , 'treshold' : 4
            }
        , 2 :
            { 'buddies_id' : 2
            , 'entity_p' : False
            , 'treshold' : 2
            }
        , 3 :
            { 'buddies_id' : 3
            , 'entity_p' : False
            , 'treshold' : 2
            }
        }
    }

"""

_test_q_result_pg = r"""
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> ET     = apt ["PAP.Appointment"]
    >>> qrt    = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> dtt    = datetime.time
    >>> inf_lu = ET.time.P_Type (None, None)
    >>> inf_u  = ET.time.P_Type (dtt (10, 0), None)

    >>> print (qrt.filter (pid = 1).attr (Q.time))
    SQL: SELECT DISTINCT pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE mom_id_entity.pid = :pid_1

    >>> print (qrt.filter (pid = 1).attr (Q.time.lower))
    SQL: SELECT DISTINCT lower(pap_appointment.time) AS lower_1
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE mom_id_entity.pid = :pid_1

    >>> show_query (qrt.filter (Q.time))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE NOT isempty(pap_appointment.time)

    >>> show_query (qrt.filter (Q.time.lower))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE lower(pap_appointment.time) IS NOT NULL

    >>> show_query (qrt.filter (Q.time.lower.minute))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE EXTRACT(minute FROM lower(pap_appointment.time))

    >>> show_query (qrt.filter (Q.time.lower == Q.time.upper))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE lower(pap_appointment.time) = upper(pap_appointment.time)

    >>> show_query (qrt.filter (ET.AQ.time.lower.AC ("08:30")))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE lower(pap_appointment.time) = :lower_1
    Parameters:
         lower_1              : datetime.datetime(1, 1, 1, 8, 30)

    >>> show_query (qrt.filter (Q.time.lower == dtt (8, 30)))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE lower(pap_appointment.time) = :lower_1
    Parameters:
         lower_1              : datetime.datetime(1, 1, 1, 8, 30)

    >>> show_query (qrt.filter (Q.time.lower.minute >= 30))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE EXTRACT(minute FROM lower(pap_appointment.time)) >= :param_1
    Parameters:
         param_1              : 30

    >>> show_query (qrt.filter (Q.time.CONTAINS (dtt (8, 45))))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time @> :time_1
    Parameters:
         time_1               : datetime.time(8, 45)

    >>> show_query (qrt.filter (Q.time.CONTAINS (Q.time)))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time @> pap_appointment.time

    >>> show_query (qrt.filter (Q.time.CONTAINS (ET.time.P_Type.from_string ("08:15, 9:30"))))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time @> :time_1
    Parameters:
         time_1               : Time_Range (datetime.time(8, 15), datetime.time(9, 30), '[)')

    >>> show_query (qrt.filter (Q.time.IN (ET.time.P_Type.from_string ("08:15, 9:30"))))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time <@ :time_1
    Parameters:
         time_1               : Time_Range (datetime.time(8, 15), datetime.time(9, 30), '[)')

    >>> show_query (qrt.filter (Q.time.OVERLAPS (ET.time.P_Type.from_string ("08:15, 9:30"))))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time && :time_1
    Parameters:
         time_1               : Time_Range (datetime.time(8, 15), datetime.time(9, 30), '[)')

    >>> print (qrt.order_by (Q.time).attrs ("time", ))
    SQL: SELECT DISTINCT pap_appointment.time AS pap_appointment_time
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         ORDER BY pap_appointment.time

    >>> print (qrt.order_by (Q.time.lower).attrs ("time.lower", "time.upper"))
    SQL: SELECT DISTINCT
           lower(pap_appointment.time) AS lower_1,
           upper(pap_appointment.time) AS upper_1
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         ORDER BY lower(pap_appointment.time)

"""

_test_q_result_sq = r"""
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> ET     = apt ["PAP.Appointment"]
    >>> qrt    = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> dtt    = datetime.time
    >>> inf_lu = ET.time.P_Type (None, None)
    >>> inf_u  = ET.time.P_Type (dtt (10, 0), None)

    >>> print (qrt.filter (pid = 1).attr (Q.time))
    SQL: SELECT DISTINCT
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE mom_id_entity.pid = :pid_1

    >>> print (qrt.filter (pid = 1).attr (Q.time.lower))
    SQL: SELECT DISTINCT pap_appointment.time__lower AS pap_appointment_time__lower
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE mom_id_entity.pid = :pid_1

    >>> show_query (qrt.filter (Q.pid.IN ([1, 2])))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE mom_id_entity.pid IN (:pid_1, :pid_2)
    Parameters:
         pid_1                : 1
         pid_2                : 2

    >>> show_query (qrt.filter (Q.time))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time__lower > pap_appointment.time__upper

    >>> show_query (qrt.filter (Q.time.lower))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time__lower IS NOT NULL

    >>> show_query (qrt.filter (Q.time.lower.minute))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE CAST(strftime(:strftime_1, pap_appointment.time__lower) AS INTEGER)
    Parameters:
         strftime_1           : '%%M'

    >>> show_query (qrt.filter (Q.time.lower == Q.time.upper))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time__lower = pap_appointment.time__upper

    >>> show_query (qrt.filter (ET.AQ.time.lower.AC ("08:30")))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time__lower = :time__lower_1
    Parameters:
         time__lower_1        : datetime.datetime(1, 1, 1, 8, 30)

    >>> show_query (qrt.filter (Q.time.lower == dtt (8, 30)))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time__lower = :time__lower_1
    Parameters:
         time__lower_1        : datetime.datetime(1, 1, 1, 8, 30)

    >>> show_query (qrt.filter (Q.time.lower.minute >= 30))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE CAST(strftime(:strftime_1, pap_appointment.time__lower) AS INTEGER) >= :param_1
    Parameters:
         param_1              : 30
         strftime_1           : '%%M'

    >>> show_query (qrt.filter (Q.time.CONTAINS (dtt (8, 45))))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE (pap_appointment.time__lower IS NULL
            OR pap_appointment.time__lower <= :time__lower_1)
            AND (pap_appointment.time__upper IS NULL
            OR pap_appointment.time__upper > :time__upper_1)
    Parameters:
         time__lower_1        : datetime.time(8, 45)
         time__upper_1        : datetime.time(8, 45)

    >>> show_query (qrt.filter (Q.time.CONTAINS (Q.time)))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE (pap_appointment.time__lower IS NULL
            OR pap_appointment.time__lower <= pap_appointment.time__lower)
            AND (pap_appointment.time__upper IS NULL
            OR pap_appointment.time__upper >= pap_appointment.time__upper)

    >>> show_query (qrt.filter (Q.time.IN (ET.time.P_Type.from_string ("08:15, 9:30"))))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time__lower >= :time__lower_1
            AND pap_appointment.time__upper <= :time__upper_1
    Parameters:
         time__lower_1        : datetime.time(8, 15)
         time__upper_1        : datetime.time(9, 30)

    >>> show_query (qrt.filter (Q.time.IN (Q.time)))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE (pap_appointment.time__lower = :time__lower_1
            OR pap_appointment.time__lower >= pap_appointment.time__lower)
            AND (pap_appointment.time__upper = :time__upper_1
            OR pap_appointment.time__upper <= pap_appointment.time__upper)
    Parameters:
         time__lower_1        : <class 'sqlalchemy.sql.elements.Null'>
         time__upper_1        : <class 'sqlalchemy.sql.elements.Null'>

    >>> show_query (qrt.filter (Q.time.IN (inf_lu)))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE 1 = 1

    >>> show_query (qrt.filter (Q.time.IN (inf_u)))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         WHERE pap_appointment.time__lower >= :time__lower_1
    Parameters:
         time__lower_1        : datetime.time(10, 0)

    >>> print (qrt.order_by (Q.time).attrs ("time", ))
    SQL: SELECT DISTINCT
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         ORDER BY pap_appointment.time__lower, pap_appointment.time__upper

    >>> print (qrt.order_by (Q.time.lower).attrs ("time.lower", ))
    SQL: SELECT DISTINCT pap_appointment.time__lower AS pap_appointment_time__lower
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
         ORDER BY pap_appointment.time__lower

    >>> print (qrt.order_by (ET.sorted_by_epk))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_appointment."left" AS pap_appointment_left,
           pap_appointment.date AS pap_appointment_date,
           pap_appointment.pid AS pap_appointment_pid,
           pap_appointment.time__lower AS pap_appointment_time__lower,
           pap_appointment.time__upper AS pap_appointment_time__upper
         FROM mom_id_entity
           JOIN pap_appointment ON mom_id_entity.pid = pap_appointment.pid
           JOIN pap_person AS pap_person__1 ON pap_person__1.pid = pap_appointment."left"
         ORDER BY pap_person__1.last_name, pap_person__1.first_name, pap_person__1.middle_name, pap_person__1.title, pap_appointment.date, pap_appointment.time__lower, pap_appointment.time__upper

"""

_test_structured = r"""
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)
    >>> ET       = apt ["PAP.Appointment"]

    >>> print (portable_repr (ET.date.attr.E_Type.edit_attr))
    ()
    >>> print (portable_repr (ET.date.attr.E_Type.q_able_no_edit))
    (Int `day`, Int `month`, Int `year`)

    >>> print (portable_repr (ET.time.attr.E_Type.edit_attr))
    (Time `lower`, Time `upper`)
    >>> print (portable_repr (ET.time.attr.E_Type.q_able_no_edit))
    ()

    >>> S = MOM.Attr.Selector.editable
    >>> print (list (S (ET.date.attr.E_Type)))
    []
    >>> print (list (S (ET.time.attr.E_Type)))
    [Time `lower`, Time `upper`]

"""

_test_tables_pg = r"""
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)
    >>> ET       = apt ["PAP.Appointment"]
    >>> qrt      = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxp      = QX.Mapper (qrt)
    >>> dtt      = datetime.time

    >>> ET.uniqueness_dbw
    [Uniqueness predicate: unique_epk ('left', 'date', 'time'), Exclusion predicate: exclusive_left_date_time ('left', 'date', 'time')]

    >>> ET.uniqueness_ems
    []

    >>> show_qx (qxp (Q.time))
    <PAP.Appointment | QX._QX_Range_ for
         <SAW : Time_Range `time` [pap_appointment.time]>>

    >>> show_qx (qxp (Q.time.CONTAINS (Q.time)))
    Call:contains:
      <PAP.Appointment | QX._QX_Range_ for
           <SAW : Time_Range `time` [pap_appointment.time]>>

    >>> show_qx (qxp (Q.time == Q.time))
    Bin:__eq__:
      <PAP.Appointment | QX._QX_Range_ for
           <SAW : Time_Range `time` [pap_appointment.time]>>
      <PAP.Appointment | QX._QX_Range_ for
           <SAW : Time_Range `time` [pap_appointment.time]>>

    >>> show_qx (qxp (Q.time.lower == dtt (8, 30)))
    Bin:__eq__:
      <time__445__type_desc | QX.Kind_Structured_Field_Extractor for
           <SAW : Time `time.lower` [lower(pap_appointment.time)]>>
          <PAP.Appointment | QX._QX_Range_ for
               <SAW : Time_Range `time` [pap_appointment.time]>>
      08:30:00

    >>> show_qx (qxp (Q.time.lower.minute == 30))
    Bin:__eq__:
      <time__445__type_desc | QX.Kind_Structured_Field_Extractor for
           <SAW : Time `time.lower` [lower(pap_appointment.time)]>>
          <PAP.Appointment | QX._QX_Range_ for
               <SAW : Time_Range `time` [pap_appointment.time]>>
      30

    >>> show_table (apt, apt._SAW.et_map ["PAP.Appointment"])
    PAP.Appointment (MOM.Id_Entity) <Table pap_appointment>
        Column date                      : Date                 Primary__Structured Date date
        Column left                      : Integer              Link_Role__Init_Only Person left Id_Entity()
        Column pid                       : Integer              Internal__Just_Once Surrogate pid primary ForeignKey('mom_id_entity.pid')
        Column time                      : Time_Range           Primary__Range__Structured Time_Range time

    >>> show_q_able_names (apt, lambda x : x.e_type.type_base_name == "Appointment")
    <SAW : PAP.Appointment [pap_appointment : mom_id_entity]>
      creation                      : creation
      date                          : date
          day                           : date.day
          month                         : date.month
          year                          : date.year
      events                        : events
      last_change                   : last_change
      last_cid                      : last_cid
      left                          : left, person
      pid                           : pid
      time                          : time
          lower                         : time.lower
              hour                          : time__lower.hour
              minute                        : time__lower.minute
              second                        : time__lower.second
          upper                         : time.upper
              hour                          : time__upper.hour
              minute                        : time__upper.minute
              second                        : time__upper.second
      type_name                     : type_name

    >>> show_q_able (apt, lambda x : x.e_type.type_base_name == "Appointment")
    <SAW : PAP.Appointment [pap_appointment : mom_id_entity]>
      <SAW : Rev_Ref `creation`>
      <SAW : Date `date` [pap_appointment.date]>
      <SAW : Int `date.day`>
      <SAW : Int `date.month`>
      <SAW : Int `date.year`>
      <SAW : Link_Ref_List `events`>
      <SAW : Rev_Ref `last_change`>
      <SAW : Int `last_cid` [mom_id_entity.last_cid]>
      <SAW : Person `left` [pap_appointment.left]>
      <SAW : Surrogate `pid` [mom_id_entity.pid]>
      <SAW : Time_Range `time` [pap_appointment.time]>
      <SAW : String `type_name` [mom_id_entity.type_name]>

    >>> show_qc_map (apt, lambda x : x.e_type.type_base_name == "Appointment")
    <SAW : PAP.Appointment [pap_appointment : mom_id_entity]>
        creation                  : <SAW : Rev_Ref `creation`>
        date                      : <Col-Mapper for <SAW : Date `date` [pap_appointment.date>
            day                   : <SAW : Int `date.day`>
            month                 : <SAW : Int `date.month`>
            year                  : <SAW : Int `date.year`>
        date.day                  : <SAW : Int `date.day`>
        date.month                : <SAW : Int `date.month`>
        date.year                 : <SAW : Int `date.year`>
        electric                  : mom_id_entity.electric
        events                    : <SAW : Link_Ref_List `events`>
        last_change               : <SAW : Rev_Ref `last_change`>
        last_cid                  : mom_id_entity.last_cid
        left                      : pap_appointment.left
        person                    : pap_appointment.left
        pid                       : mom_id_entity.pid
        time                      : <Col-Mapper for <SAW : Time_Range `time` [pap_appointmen>
            time.lower            : <Col-Mapper for <SAW : Time `time.lower` [time__lower]> >
                hour              : <SAW : Int `time__lower.hour`>
                minute            : <SAW : Int `time__lower.minute`>
                second            : <SAW : Int `time__lower.second`>
            time.upper            : <Col-Mapper for <SAW : Time `time.upper` [time__upper]> >
                hour              : <SAW : Int `time__upper.hour`>
                minute            : <SAW : Int `time__upper.minute`>
                second            : <SAW : Int `time__upper.second`>
            time__lower.hour      : <SAW : Int `time__lower.hour`>
            time__lower.minute    : <SAW : Int `time__lower.minute`>
            time__lower.second    : <SAW : Int `time__lower.second`>
            time__upper.hour      : <SAW : Int `time__upper.hour`>
            time__upper.minute    : <SAW : Int `time__upper.minute`>
            time__upper.second    : <SAW : Int `time__upper.second`>
        time.lower                : <SAW : Time `time.lower` [time__lower]>
        time.upper                : <SAW : Time `time.upper` [time__upper]>
        type_name                 : mom_id_entity.type_name
        x_locked                  : mom_id_entity.x_locked

"""

_test_tables_sq = r"""
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)
    >>> ET       = apt ["PAP.Appointment"]
    >>> qrt      = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxp      = QX.Mapper (qrt)
    >>> dtt      = datetime.time

    >>> ET.uniqueness_dbw
    [Uniqueness predicate: unique_epk ('left', 'date', 'time')]

    >>> ET.uniqueness_ems
    [Exclusion predicate: exclusive_left_date_time ('left', 'date', 'time')]

    >>> show_qx (qxp (Q.time))
    <time__445__type_desc | QX._QX_Range_ for
         <SAW : Time_Range `time` [pap_appointment.time__lower, pap_appointment.time__upper]>>

    >>> show_qx (qxp (Q.time.CONTAINS (Q.time)))
    Call:contains:
      <time__445__type_desc | QX._QX_Range_ for
           <SAW : Time_Range `time` [pap_appointment.time__lower, pap_appointment.time__upper]>>

    >>> show_qx (qxp (Q.time == Q.time))
    Bin:__eq__:
      <time__445__type_desc | QX._QX_Range_ for
           <SAW : Time_Range `time` [pap_appointment.time__lower, pap_appointment.time__upper]>>
      <time__445__type_desc | QX._QX_Range_ for
           <SAW : Time_Range `time` [pap_appointment.time__lower, pap_appointment.time__upper]>>

    >>> show_qx (qxp (Q.time.lower == dtt (8, 30)))
    Bin:__eq__:
      <time__445__type_desc | QX.Kind_Structured_Field_Extractor for
           <SAW : Time `time.lower` [pap_appointment.time__lower]>>
          <time__445__type_desc | QX._QX_Range_ for
               <SAW : Time_Range `time` [pap_appointment.time__lower, pap_appointment.time__upper]>>
      08:30:00

    >>> show_qx (qxp (Q.time.lower.minute == 30))
    Bin:__eq__:
      <time__445__type_desc | QX.Kind_Structured_Field_Extractor for
           <SAW : Time `time.lower` [pap_appointment.time__lower]>>
          <time__445__type_desc | QX._QX_Range_ for
               <SAW : Time_Range `time` [pap_appointment.time__lower, pap_appointment.time__upper]>>
      30

    >>> show_table (apt, apt._SAW.et_map ["PAP.Appointment"])
    PAP.Appointment (MOM.Id_Entity) <Table pap_appointment>
        Column date                      : Date                 Primary__Structured Date date
        Column left                      : Integer              Link_Role__Init_Only Person left Id_Entity()
        Column pid                       : Integer              Internal__Just_Once Surrogate pid primary ForeignKey('mom_id_entity.pid')
        Column time__lower               : Datetime             Optional__Structured Time lower
        Column time__upper               : Datetime             Optional__Structured Time upper

    >>> show_q_able_names (apt, lambda x : x.e_type.type_base_name == "Appointment")
    <SAW : PAP.Appointment [pap_appointment : mom_id_entity]>
      creation                      : creation
      date                          : date
          day                           : date.day
          month                         : date.month
          year                          : date.year
      events                        : events
      last_change                   : last_change
      last_cid                      : last_cid
      left                          : left, person
      pid                           : pid
      time                          : time
          lower                         : time.lower
              hour                          : time__lower.hour
              minute                        : time__lower.minute
              second                        : time__lower.second
          upper                         : time.upper
              hour                          : time__upper.hour
              minute                        : time__upper.minute
              second                        : time__upper.second
      type_name                     : type_name

    >>> show_q_able (apt, lambda x : x.e_type.type_base_name == "Appointment")
    <SAW : PAP.Appointment [pap_appointment : mom_id_entity]>
      <SAW : Rev_Ref `creation`>
      <SAW : Date `date` [pap_appointment.date]>
      <SAW : Int `date.day`>
      <SAW : Int `date.month`>
      <SAW : Int `date.year`>
      <SAW : Link_Ref_List `events`>
      <SAW : Rev_Ref `last_change`>
      <SAW : Int `last_cid` [mom_id_entity.last_cid]>
      <SAW : Person `left` [pap_appointment.left]>
      <SAW : Surrogate `pid` [mom_id_entity.pid]>
      <SAW : Time_Range `time` [pap_appointment.time__lower, pap_appointment.time__upper]>
      <SAW : String `type_name` [mom_id_entity.type_name]>

    >>> show_qc_map (apt, lambda x : x.e_type.type_base_name == "Appointment")
    <SAW : PAP.Appointment [pap_appointment : mom_id_entity]>
        creation                  : <SAW : Rev_Ref `creation`>
        date                      : <Col-Mapper for <SAW : Date `date` [pap_appointment.date>
            day                   : <SAW : Int `date.day`>
            month                 : <SAW : Int `date.month`>
            year                  : <SAW : Int `date.year`>
        date.day                  : <SAW : Int `date.day`>
        date.month                : <SAW : Int `date.month`>
        date.year                 : <SAW : Int `date.year`>
        electric                  : mom_id_entity.electric
        events                    : <SAW : Link_Ref_List `events`>
        last_change               : <SAW : Rev_Ref `last_change`>
        last_cid                  : mom_id_entity.last_cid
        left                      : pap_appointment.left
        person                    : pap_appointment.left
        pid                       : mom_id_entity.pid
        time                      : <Col-Mapper for time__445__type_desc>
            time.lower            : <Col-Mapper for <SAW : Time `time.lower` [pap_appointmen>
                hour              : <SAW : Int `time__lower.hour`>
                minute            : <SAW : Int `time__lower.minute`>
                second            : <SAW : Int `time__lower.second`>
            time.upper            : <Col-Mapper for <SAW : Time `time.upper` [pap_appointmen>
                hour              : <SAW : Int `time__upper.hour`>
                minute            : <SAW : Int `time__upper.minute`>
                second            : <SAW : Int `time__upper.second`>
            time__lower.hour      : <SAW : Int `time__lower.hour`>
            time__lower.minute    : <SAW : Int `time__lower.minute`>
            time__lower.second    : <SAW : Int `time__lower.second`>
            time__upper.hour      : <SAW : Int `time__upper.hour`>
            time__upper.minute    : <SAW : Int `time__upper.minute`>
            time__upper.second    : <SAW : Int `time__upper.second`>
        time.lower                : pap_appointment.time__lower
        time.upper                : pap_appointment.time__upper
        type_name                 : mom_id_entity.type_name
        x_locked                  : mom_id_entity.x_locked

    >>> show_xs_filter (apt, "PAP.Appointment", Q.time.lower == "08:30")
    PAP.Appointment  :  Q.time.lower == '08:30'
        pap_appointment.time__lower = :time__lower_1

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( main          = _test_main
        , mf3           = _test_MF3
        , structured    = _test_structured
        )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            (
            )
        , ignore = ("HPS", )
        )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( attr_wrappers_pg = _test_attr_wrappers_pg
            , q_result_pg      = _test_q_result_pg
            , tables_pg        = _test_tables_pg
            )
        , ignore = ("HPS", "MYS", "SQL", "sq")
        )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( attr_wrappers_sq = _test_attr_wrappers_sq
            , q_result_sq      = _test_q_result_sq
            , tables_sq        = _test_tables_sq
            )
        , ignore = ("HPS", "MYS", "POS", "pg")
        )
    )

### __END__ GTW.__test__.Attr_Range
