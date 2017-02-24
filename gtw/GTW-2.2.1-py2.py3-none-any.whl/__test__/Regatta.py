# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.__test__.Regatta
#
# Purpose
#    Test Regatta creation and querying
#
# Revision Dates
#    30-Apr-2010 (CT) Creation
#     9-Sep-2011 (CT) Test for `Q.RAW.left.date.start` added
#    15-Nov-2011 (CT) Add tests for `sorted_by` and `sort_key`
#    19-Mar-2012 (CT) Adapt to `Boat_Class.name.ignore_case` now being `True`
#    19-Mar-2012 (CT) Adapt to reification of `SRM.Handicap`
#    29-Mar-2012 (CT) Add test for cached role `regattas`
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    ««revision-date»»···
#--

from   __future__               import print_function

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM = scope.SRM
    >>> PAP = scope.PAP
    >>> p = PAP.Person ("Tanzer", "Christian")
    >>> bc  = SRM.Boat_Class (u"Optimist", max_crew = 1)
    >>> ys  = SRM.Handicap ("Yardstick")
    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", ("20080501", ), raw = True)
    >>> prepr (rev.epk_raw)
    ('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event')
    >>> SRM.Regatta_Event.instance (* rev.epk_raw, raw = True)
    SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'))
    >>> SRM.Regatta_Event.instance (* rev.epk)
    SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'))
    >>> reg = SRM.Regatta_C (rev.epk_raw, boat_class = bc.epk_raw, result = ("2008-05-01 06:00 +02:00", ), raw = True)
    >>> prepr (reg.epk_raw)
    (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    >>> SRM.Regatta_C.instance (* reg.epk_raw, raw = True)
    SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))
    >>> SRM.Regatta_C.instance (* reg.epk)
    SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))
    >>> reh = SRM.Regatta_H (rev.epk_raw, ys,  raw = True)
    >>> prepr (reh.epk_raw)
    (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Yardstick', 'SRM.Handicap'), 'SRM.Regatta_H')
    >>> SRM.Regatta_H.instance (* reh.epk_raw, raw = True)
    SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))
    >>> SRM.Regatta_H.instance (* reh.epk)
    SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))

    >>> reg.result
    SRM.Regatta_Result ('2008-05-01 04:00')

    >>> TFL.user_config.time_zone = None
    >>> reg.__class__.result.E_Type.date.as_rest_cargo_ckd (reg.result)
    '2008-05-01T04:00:00+00:00'
    >>> reg.__class__.result.E_Type.date.as_rest_cargo_raw (reg.result)
    '2008-05-01 04:00'

    >>> TFL.user_config.time_zone = "Europe/Vienna"
    >>> reg.__class__.result.E_Type.date.as_rest_cargo_ckd (reg.result)
    '2008-05-01T06:00:00+02:00'
    >>> reg.__class__.result.E_Type.date.as_rest_cargo_raw (reg.result)
    '2008-05-01 06:00'

    >>> TFL.user_config.time_zone = "America/New_York"
    >>> reg.__class__.result.E_Type.date.as_rest_cargo_ckd (reg.result)
    '2008-05-01T00:00:00-04:00'
    >>> reg.__class__.result.E_Type.date.as_rest_cargo_raw (reg.result)
    '2008-05-01'

    >>> SRM.Regatta.query_s (Q.RAW.left.date.start == "2008-05-01").all ()
    [SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))]

    >>> print (reg.sorted_by)
    <Sorted_By: Getter function for `.left.name`, Getter function for `.left.date.start`, Getter function for `.left.date.finish`, Getter function for `.boat_class.name`>
    >>> print (reh.sorted_by)
    <Sorted_By: Getter function for `.left.name`, Getter function for `.left.date.start`, Getter function for `.left.date.finish`, Getter function for `.boat_class.name`>

    >>> sk = TFL.Sorted_By (scope.MOM.Id_Entity.sort_key)
    >>> prepr (sk (reg))
    (('tuple', (('tuple', ('text-string', 'himmelfahrt')), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('text-string', 'optimist')))),)
    >>> prepr (sk (reh))
    (('tuple', (('tuple', ('text-string', 'himmelfahrt')), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('text-string', 'yardstick')))),)

    >>> SRM.Regatta.query_s (Q.RAW.left.date.start == "2008-05-01").order_by (sk).all ()
    [SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))]

    >>> scope.MOM.Id_Entity.query_s ().order_by (sk).all ()
    [SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01')), SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', )), SRM.Boat_Class ('optimist'), PAP.Person ('tanzer', 'christian', '', ''), SRM.Handicap ('yardstick')]

    >>> for x in scope.MOM.Id_Entity.query_s ().order_by (sk) :
    ...    print (x, NL, "   ", portable_repr (sk (x)))
    ('himmelfahrt', ('2008-05-01', '2008-05-01'))
         (('tuple', (('tuple', ('text-string', 'himmelfahrt')), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('date', datetime.date(2008, 5, 1))))),)
    (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))
         (('tuple', (('tuple', ('text-string', 'himmelfahrt')), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('text-string', 'optimist')))),)
    (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))
         (('tuple', (('tuple', ('text-string', 'himmelfahrt')), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('date', datetime.date(2008, 5, 1))), ('tuple', ('text-string', 'yardstick')))),)
    ('optimist')
         (('tuple', (('tuple', ('text-string', 'optimist')),)),)
    ('tanzer', 'christian', '', '')
         (('tuple', (('tuple', ('text-string', 'tanzer')), ('tuple', ('text-string', 'christian')), ('tuple', ('text-string', '')), ('tuple', ('text-string', '')))),)
    ('yardstick')
         (('tuple', (('tuple', ('text-string', 'yardstick')),)),)

#    ### XXX auto cached roles are currently not supported
#    ### XXX * either remove tests or re-add auto-cached roles and fix tests
#    >>> sorted (SRM.Regatta.acr_map.values ())
#    [<Link_Cacher_n (GTW.OMP.SRM.Regatta) event --> regattas>]
#    >>> sorted (SRM.Regatta_C.acr_map.values ())
#    [<Link_Cacher_n (GTW.OMP.SRM.Regatta_C) event --> regattas>]
#    >>> sorted (SRM.Regatta_H.acr_map.values ())
#    [<Link_Cacher_n (GTW.OMP.SRM.Regatta_H) event --> regattas>]

    >>> crs = SRM.Regatta_Event.regattas
    >>> print (crs, ":", crs.Ref_Type.type_name)
    Link_Ref_List `regattas` : SRM.Regatta

    >>> sorted (rev.regattas, key = TFL.Sorted_By ())
    [SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))]

"""

from _GTW.__test__.model import *
NL = chr (10)

import _TFL.User_Config

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.Regatta
