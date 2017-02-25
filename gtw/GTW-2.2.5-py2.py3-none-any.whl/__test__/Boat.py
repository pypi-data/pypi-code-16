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
#    GTW.__test__.Boat
#
# Purpose
#    Test SRM.Boat creation and querying
#
# Revision Dates
#    27-Apr-2010 (CT) Creation
#    29-Mar-2011 (CT) Test for change of `Init_Only_Mixin` attribute added
#     9-Nov-2011 (CT) Add test for `sail_number_head` and `sail_number_tail`
#    10-Nov-2011 (CT) Add test for `Name_Clash`
#    19-Mar-2012 (CT) Adapt to `Boat_Class.name.ignore_case` now being `True`
#    12-Apr-2012 (CT) Add tests for `max_crew` predicate
#    12-Apr-2012 (CT) Add tests for `on_error`
#    15-Apr-2012 (CT) Adapt to changes of `MOM.Error`
#    17-Apr-2012 (CT) Adapt to more changes of `MOM.Error`
#     2-Jul-2012 (MG) Additional tests for handling of execptions added
#     9-Sep-2012 (MG) Test for `convert_creation_change` added
#     9-Sep-2012 (RS) Add `last_changed` and `creation_date` checks
#    30-Jan-2013 (CT) Adapt to `Unique` predicates
#     3-Jun-2013 (CT) Add `_test_instances_committed`, `_test_instances_pending`
#    11-Feb-2015 (CT) Remove test for `sail_number_head` and `sail_number_tail`
#    ««revision-date»»···
#--

from   __future__               import print_function

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM = scope.SRM

    >>> bc = SRM.Boat_Class ("Optimist", max_crew = 1)
    >>> bc
    SRM.Boat_Class ('optimist')

    >>> bc.pid
    1
    >>> scope.commit ()

    >>> scope.SRM.Boat_Class.query ().all ()
    [SRM.Boat_Class ('optimist')]
    >>> change = scope.query_changes (pid = bc.pid).one ()
    >>> change.c_time == change.time, change.c_user ==change.user
    (True, True)
    >>> c_time = datetime.datetime (2012, 1, 1,  0, 0, 0)
    >>> time   = datetime.datetime (2012, 4, 1, 10, 0, 0)
    >>> scope.ems.convert_creation_change \
        (bc.pid, c_time = c_time, time = time, user = 42, c_user = 23)
    >>> change = scope.query_changes (pid = bc.pid).one ()
    >>> prepr ((change.c_user, change.c_time, change.user, change.time)) ### before commit
    (23, datetime.datetime(2012, 1, 1, 0, 0), 42, datetime.datetime(2012, 4, 1, 10, 0))

    >>> bc.last_change.time
    datetime.datetime(2012, 4, 1, 10, 0)
    >>> bc.last_changed
    datetime.datetime(2012, 4, 1, 10, 0)
    >>> bc.creation.c_time
    datetime.datetime(2012, 1, 1, 0, 0)
    >>> bc.creation_date
    datetime.datetime(2012, 1, 1, 0, 0)

    >>> print (scope.SRM.Boat_Class.count) ### 1
    1
    >>> laser = SRM.Boat_Class ("Laser", max_crew = 1)
    >>> print (scope.SRM.Boat_Class.count) ### 2
    2

    >>> scope.SRM.Boat_Class.query (name = 'optimist').all ()
    [SRM.Boat_Class ('optimist')]
    >>> scope.SRM.Boat_Class.instance ('Optimist')
    SRM.Boat_Class ('optimist')
    >>> SRM.Boat.instance_or_new ('Optimist', "1107", "AUT", raw = True) ### 1
    SRM.Boat (('optimist', ), 1107, 'AUT', '')
    >>> print (scope.SRM.Boat.count) ### 3
    1
    >>> scope.SRM.Boat.query_s ().all ()
    [SRM.Boat (('optimist', ), 1107, 'AUT', '')]
    >>> scope.commit ()

    >>> change = scope.query_changes (pid = bc.pid).one ()
    >>> prepr ((change.c_user, change.c_time, change.user, change.time)) ### after commit
    (23, datetime.datetime(2012, 1, 1, 0, 0), 42, datetime.datetime(2012, 4, 1, 10, 0))

    >>> SRM.Boat.instance_or_new ('Optimist', "1107", "AUT", raw = True) ### 2
    SRM.Boat (('optimist', ), 1107, 'AUT', '')
    >>> print (scope.SRM.Boat.count) ### 4
    1
    >>> scope.SRM.Boat.query_s ().all ()
    [SRM.Boat (('optimist', ), 1107, 'AUT', '')]

    >>> b = SRM.Boat.instance_or_new ('Optimist', "1107", "AUT", raw = True) ### 3
    >>> c = SRM.Boat ("Optimist", "42", None, "OE", raw = True)

    >>> print (scope.SRM.Boat.count) ### 5
    2
    >>> scope.SRM.Boat.query_s ().all ()
    [SRM.Boat (('optimist', ), 42, '', 'OE'), SRM.Boat (('optimist', ), 1107, 'AUT', '')]

    >>> s1 = TFL.Sorted_By ("name")
    >>> s2 = TFL.Sorted_By ("-name")
    >>> SRM.Boat_Class.query ().order_by (s1).all ()
    [SRM.Boat_Class ('laser'), SRM.Boat_Class ('optimist')]
    >>> SRM.Boat_Class.query ().order_by (s1).order_by (s2).all ()
    [SRM.Boat_Class ('optimist'), SRM.Boat_Class ('laser')]

    >>> prepr (SRM.Boat.sail_number.Q_Raw.EQ)
    <Attr.Equal sail_number.EQ [==]>
    >>> rf = SRM.Boat.sail_number.Q_Raw.EQ ("1107")
    >>> rf (b)
    True

    >>> prepr (getattr (b, "__raw_sail_number", "No raw value???"))
    '1107'

    >>> print (SRM.Boat.sail_number.Q_Raw.EQ  ("1107"))
    Q.sail_number == 1107
    >>> print (SRM.Boat.sail_number.Q_Raw.EQS ("1107"))
    Q.__raw_sail_number == '1107'
    >>> print (SRM.Boat.sail_number.Q_Raw.AC  ("11"))
    Q.__raw_sail_number.startswith ('11',)

    >>> bq = SRM.Boat.query_s ()
    >>> bq.all ()
    [SRM.Boat (('optimist', ), 42, '', 'OE'), SRM.Boat (('optimist', ), 1107, 'AUT', '')]
    >>> SRM.Boat.query_s (SRM.Boat.sail_number.Q_Raw.EQ ("1107")).all ()
    [SRM.Boat (('optimist', ), 1107, 'AUT', '')]
    >>> SRM.Boat.query_s (SRM.Boat.sail_number.Q_Raw.AC ("11")).all ()
    [SRM.Boat (('optimist', ), 1107, 'AUT', '')]

    >>> print (scope.SRM.Boat.count) ### 6
    2

    >>> b.set (left = laser)
    Traceback (most recent call last):
      ...
    AttributeError: Init-only attribute `Boat.left` cannot be changed from `('optimist')` to `('laser')` after object creation

    >>> print (scope.SRM.Boat.count) ### 7
    2
    >>> scope.commit ()

    >>> SRM.Boat.query_s ().all () ### before Name_Clash
    [SRM.Boat (('optimist', ), 42, '', 'OE'), SRM.Boat (('optimist', ), 1107, 'AUT', '')]

    >>> laser.max_crew ### before name clash, before change
    1
    >>> laser.max_crew = 2
    >>> laser.max_crew ### before name clash, after change
    2
    >>> with expect_except (MOM.Error.Invariants) :
    ...     d = SRM.Boat (SRM.Boat_Class ("Optimist", max_crew = 1), "AUT", "1134")
    Invariants: The attribute values for 'name' must be unique for each object
      The new definition of Boat_Class SRM.Boat_Class ('Optimist',) would clash with 1 existing entities
      Already existing:
        SRM.Boat_Class ('Optimist',)

    >>> print (scope.SRM.Boat.count) ### 8
    2
    >>> laser.max_crew ### after name clash
    2

    >>> SRM.Boat.query_s ().all () ### after Name_Clash
    [SRM.Boat (('optimist', ), 42, '', 'OE'), SRM.Boat (('optimist', ), 1107, 'AUT', '')]

    >>> prepr (sorted (b.b_class._pred_man.errors.items ())) ### before invariant errors
    [('exclusion', []), ('object', []), ('object_init', []), ('region', []), ('system', []), ('uniqueness', [])]

    >>> with expect_except (MOM.Error.Invariant) :
    ...     b.b_class.max_crew = 0
    Invariant: Condition `AC_check_max_crew_0` : 1 <= max_crew <= 4
        max_crew = 0
    >>> prepr (sorted (b.b_class._pred_man.errors.items ())) ### after invariant error from `setattr`
    [('exclusion', []), ('object', []), ('object_init', []), ('region', []), ('system', []), ('uniqueness', [])]


    >>> errors = []
    >>> with expect_except (MOM.Error.Invariants) :
    ...     b.b_class.set (max_crew = 0)
    Invariants: Condition `AC_check_max_crew_0` : 1 <= max_crew <= 4
        max_crew = 0
    >>> prepr (sorted (b.b_class._pred_man.errors.items ())) ### after invariant error from `.set (max_crew = 0)`
    [('exclusion', []), ('object', [<Invariant: SRM.Boat_Class ('Optimist',), Condition `AC_check_max_crew_0` : 1 <= max_crew <= 4
        max_crew = 0>]), ('object_init', []), ('region', []), ('system', []), ('uniqueness', [])]
    >>> errors
    []
    >>> b.b_class.set (max_crew = 5, on_error = errors.append)
    0
    >>> prepr (sorted (b.b_class._pred_man.errors.items ())) ### after invariant error from `.set (max_crew = 5)`
    [('exclusion', []), ('object', [<Invariant: SRM.Boat_Class ('Optimist',), Condition `AC_check_max_crew_0` : 1 <= max_crew <= 4
        max_crew = 5>]), ('object_init', []), ('region', []), ('system', []), ('uniqueness', [])]
    >>> errors
    [<Invariants: <Invariant: SRM.Boat_Class ('Optimist',), Condition `AC_check_max_crew_0` : 1 <= max_crew <= 4
        max_crew = 5>>]
    >>> print (formatted (MOM.Error.as_json_cargo (* errors)))
    [ { 'attributes' : ['max_crew']
      , 'bindings' :
          [ ( 'max_crew'
            , '5'
            )
          ]
      , 'head' : '1 <= max_crew <= 4'
      }
    ]

    >>> errors = []
    >>> with expect_except (MOM.Error.Invariants, save_error = errors) :
    ...     SRM.Boat_Class (max_crew = 4)
    Invariants: Boat_Class needs the attribute: ('name',); Instead it got: (max_crew = 4)
    >>> errors
    [<Invariants: <Required_Missing: (Boat_Class needs the attribute: ('name',); Instead it got: (max_crew = 4)>>]
    >>> print (formatted (MOM.Error.as_json_cargo (* errors)))
    [ { 'attributes' : ('name', )
      , 'bindings' :
          [ ( 'max_crew'
            , 4
            )
          , ( 'name'
            , None
            )
          ]
      , 'description' : 'Instead it got: (max_crew = 4)'
      , 'explanation' : 'All required attributes must be supplied'
      , 'head' : "Boat_Class needs the attribute: ('name',)"
      , 'is_required' : True
      }
    ]

    >>> errors = []
    >>> with expect_except (MOM.Error.Invariants, save_error = errors) :
    ...     SRM.Boat_Class ()
    Invariants: Condition `name_not_empty` : The attribute name needs a non-empty value
        name = None

    >>> errors
    [<Invariants: <Required_Empty: SRM.Boat_Class ('',), Condition `name_not_empty` : The attribute name needs a non-empty value
          name = None>>]

    >>> errors = []
    >>> with expect_except (MOM.Error.Invariants, save_error = errors) :
    ...     SRM.Boat (sail_number = "187042", raw = True)
    Invariants: Boat needs the attributes: ('left', 'sail_number'); Instead it got: (sail_number = 187042)
    >>> print (formatted (MOM.Error.as_json_cargo (* errors)))
    [ { 'attributes' : ('left', )
      , 'bindings' :
          [ ( 'left'
            , None
            )
          , ( 'sail_number'
            , '187042'
            )
          ]
      , 'description' : 'Instead it got: (sail_number = 187042)'
      , 'explanation' : 'All required attributes must be supplied'
      , 'head' : "Boat needs the attributes: ('left', 'sail_number')"
      , 'is_required' : True
      , 'missing_t' : {'left' : ['name']}
      }
    ]

    >>> errors = []
    >>> with expect_except (MOM.Error.Invariants, save_error = errors) :
    ...     SRM.Boat (sail_number = "-187042", raw = True)
    Invariants: Condition `AC_check_sail_number_1` : 0 <= sail_number <= 999999
        sail_number = -187042

    >>> print (formatted (MOM.Error.as_json_cargo (* errors)))
    [ { 'attributes' : ['sail_number']
      , 'bindings' :
          [ ( 'sail_number'
            , '-187042'
            )
          ]
      , 'head' : '0 <= sail_number <= 999999'
      , 'is_required' : True
      }
    ]

"""

_test_instances_committed = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM = scope.SRM

    >>> opti = SRM.Boat_Class ("Optimist", max_crew = 1)
    >>> opti
    SRM.Boat_Class ('optimist')
    >>> laser = SRM.Boat_Class ("Laser", max_crew = 1)
    >>> b = SRM.Boat.instance_or_new (opti, "1107", "AUT", raw = True)
    >>> c = SRM.Boat ("Optimist", "42", None, "OE", raw = True)

    >>> scope.commit ()

    >>> show_by_pid (scope.SRM.Boat_Class)
    1   : Boat_Class ('Optimist', 'SRM.Boat_Class')
    2   : Boat_Class ('Laser', 'SRM.Boat_Class')

    >>> show_by_pid (scope.SRM.Boat)
    3   : Boat       (('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat')
    4   : Boat       (('Optimist', 'SRM.Boat_Class'), '42', '', 'OE', 'SRM.Boat')

"""

_test_instances_pending = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM = scope.SRM

    >>> opti = SRM.Boat_Class ("Optimist", max_crew = 1)
    >>> opti
    SRM.Boat_Class ('optimist')
    >>> laser = SRM.Boat_Class ("Laser", max_crew = 1)
    >>> b = SRM.Boat.instance_or_new (opti, "1107", "AUT", raw = True)
    >>> c = SRM.Boat ("Optimist", "42", None, "OE", raw = True)

    >>> show_by_pid (scope.SRM.Boat_Class)
    1   : Boat_Class ('Optimist', 'SRM.Boat_Class')
    2   : Boat_Class ('Laser', 'SRM.Boat_Class')

    >>> show_by_pid (scope.SRM.Boat)
    3   : Boat       (('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat')
    4   : Boat       (('Optimist', 'SRM.Boat_Class'), '42', '', 'OE', 'SRM.Boat')

"""

def show_by_pid (ETM) :
    for x in ETM.query ().order_by (Q.pid) :
        print \
            ( "%-3s : %-10s %s"
            % (x.pid, x.type_base_name, portable_repr (x.epk_raw))
            )
# end def show_by_pid

from _GTW.__test__.model import *
import datetime

__test__ = Scaffold.create_test_dict \
    ( dict
        ( committed = _test_instances_committed
        , pending   = _test_instances_pending
        , main      = _test_code
        )
    )

### __END__ GTW.__test__.Boat
