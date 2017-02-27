# -*- coding: utf-8 -*-
# Copyright (C) 2011-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Query_Restriction
#
# Purpose
#    Test cases for GTW.RST.TOP.MOM.Query_Restriction
#
# Revision Dates
#    14-Nov-2011 (CT) Creation
#     2-Dec-2011 (CT) Creation continued..
#    19-Mar-2012 (CT) Adapt to reification of `SRM.Handicap`
#    30-Jul-2012 (CT) Change to test `GTW.RST.TOP.MOM` instead of `GTW.NAV`
#    25-Mar-2013 (CT) Add `test_pepk`
#    27-Mar-2013 (CT) Add `test_request_get` and real query to `test_pepk`
#     2-Mar-2014 (CT) Add test for `qrs.As_Json_Cargo` of `PAP.Person`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    20-May-2016 (CT) Move backend-specific test to `test_filters_q`
#     1-Jun-2016 (CT) Factor `fake_request` to `Test_Command`
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM

    >>> qe = QR.from_request (scope, PAP.Person.E_Type, f_req (qux = "42", qix = "Miles"))
    >>> print (qe.limit, qe.offset, qe.filters)
    0 0 ()

    >>> rd = f_req (
    ...   limit = 24, last_name___GE = "Qux", lifetime__start___EQ = "2008", foo = "bar")
    >>> qr = QR.from_request (scope, PAP.Person.E_Type, rd)
    >>> print (qr.limit, qr.offset)
    24 0

    >>> print (formatted (qr.filters_q))
    ( Q.last_name >= 'qux'
    , Q.lifetime.start.between (datetime.date(2008, 1, 1), datetime.date(2008, 12, 31))
    )

    >>> print (formatted (qr.filters))
    ( Record
        ( AQ = <last_name.AQ [Attr.Type.Querier String_FL]>
        , attr = String `last_name`
        , edit = 'Qux'
        , full_name = 'last_name'
        , id = 'last_name___GE'
        , name = 'last_name___GE'
        , op =
          Record
            ( desc = 'Select entities where the attribute is greater than, or equal to, the specified value'
            , label = '&ge;'
            )
        , sig_key = 3
        , ui_name = 'Last name'
        , value = 'Qux'
        )
    , Record
        ( AQ = <lifetime.start.AQ [Attr.Type.Querier Date]>
        , attr = Date `start`
        , attrs =
          [ Record
              ( attr = Int `day`
              , full_name = 'lifetime.start.day'
              , id = 'lifetime__start__day'
              , name = 'day'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Day'
              )
          , Record
              ( attr = Int `month`
              , full_name = 'lifetime.start.month'
              , id = 'lifetime__start__month'
              , name = 'month'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Month'
              )
          , Record
              ( attr = Int `year`
              , full_name = 'lifetime.start.year'
              , id = 'lifetime__start__year'
              , name = 'year'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Year'
              )
          ]
        , edit = '2008'
        , full_name = 'lifetime.start'
        , id = 'lifetime__start___EQ'
        , name = 'lifetime__start___EQ'
        , op =
          Record
            ( desc = 'Select entities where the attribute is equal to the specified value'
            , label = '&equiv;'
            )
        , sig_key = 0
        , ui_name = 'Lifetime/Start'
        , value = '2008'
        )
    )

    >>> print (formatted (qr.Filter (PAP.Person.E_Type, "last_name")))
    Record
      ( AQ = <last_name.AQ [Attr.Type.Querier String_FL]>
      , attr = String `last_name`
      , edit = None
      , full_name = 'last_name'
      , id = 'last_name___AC'
      , name = 'last_name___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Last name'
      , value = None
      )

    >>> print (formatted (qr.Filter (PAP.Person.E_Type, "last_name___GE")))
    Record
      ( AQ = <last_name.AQ [Attr.Type.Querier String_FL]>
      , attr = String `last_name`
      , edit = None
      , full_name = 'last_name'
      , id = 'last_name___GE'
      , name = 'last_name___GE'
      , op =
        Record
          ( desc = 'Select entities where the attribute is greater than, or equal to, the specified value'
          , label = '&ge;'
          )
      , sig_key = 3
      , ui_name = 'Last name'
      , value = None
      )

    >>> print (formatted (qr.filters))
    ( Record
        ( AQ = <last_name.AQ [Attr.Type.Querier String_FL]>
        , attr = String `last_name`
        , edit = 'Qux'
        , full_name = 'last_name'
        , id = 'last_name___GE'
        , name = 'last_name___GE'
        , op =
          Record
            ( desc = 'Select entities where the attribute is greater than, or equal to, the specified value'
            , label = '&ge;'
            )
        , sig_key = 3
        , ui_name = 'Last name'
        , value = 'Qux'
        )
    , Record
        ( AQ = <lifetime.start.AQ [Attr.Type.Querier Date]>
        , attr = Date `start`
        , attrs =
          [ Record
              ( attr = Int `day`
              , full_name = 'lifetime.start.day'
              , id = 'lifetime__start__day'
              , name = 'day'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Day'
              )
          , Record
              ( attr = Int `month`
              , full_name = 'lifetime.start.month'
              , id = 'lifetime__start__month'
              , name = 'month'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Month'
              )
          , Record
              ( attr = Int `year`
              , full_name = 'lifetime.start.year'
              , id = 'lifetime__start__year'
              , name = 'year'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Year'
              )
          ]
        , edit = '2008'
        , full_name = 'lifetime.start'
        , id = 'lifetime__start___EQ'
        , name = 'lifetime__start___EQ'
        , op =
          Record
            ( desc = 'Select entities where the attribute is equal to the specified value'
            , label = '&equiv;'
            )
        , sig_key = 0
        , ui_name = 'Lifetime/Start'
        , value = '2008'
        )
    )

    >>> print (qr.filters_q)
    (Q.last_name >= 'qux', Q.lifetime.start.between (datetime.date(2008, 1, 1), datetime.date(2008, 12, 31)))

    >>> qo = QR.from_request (scope, PAP.Person.E_Type, f_req (order_by = "-lifetime,last_name"))
    >>> print (formatted (qo.order_by))
    ( Record
        ( attr = Date_Interval `lifetime`
        , attrs =
          [ Record
              ( attr = Date `start`
              , attrs =
                [ Record
                    ( attr = Int `day`
                    , full_name = 'lifetime.start.day'
                    , id = 'lifetime__start__day'
                    , name = 'day'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Day'
                    )
                , Record
                    ( attr = Int `month`
                    , full_name = 'lifetime.start.month'
                    , id = 'lifetime__start__month'
                    , name = 'month'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Month'
                    )
                , Record
                    ( attr = Int `year`
                    , full_name = 'lifetime.start.year'
                    , id = 'lifetime__start__year'
                    , name = 'year'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Year'
                    )
                ]
              , full_name = 'lifetime.start'
              , id = 'lifetime__start'
              , name = 'start'
              , sig_key = 0
              , ui_name = 'Lifetime/Start'
              )
          , Record
              ( attr = Date `finish`
              , attrs =
                [ Record
                    ( attr = Int `day`
                    , full_name = 'lifetime.finish.day'
                    , id = 'lifetime__finish__day'
                    , name = 'day'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Day'
                    )
                , Record
                    ( attr = Int `month`
                    , full_name = 'lifetime.finish.month'
                    , id = 'lifetime__finish__month'
                    , name = 'month'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Month'
                    )
                , Record
                    ( attr = Int `year`
                    , full_name = 'lifetime.finish.year'
                    , id = 'lifetime__finish__year'
                    , name = 'year'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Year'
                    )
                ]
              , full_name = 'lifetime.finish'
              , id = 'lifetime__finish'
              , name = 'finish'
              , sig_key = 0
              , ui_name = 'Lifetime/Finish'
              )
          , Record
              ( attr = Boolean `alive`
              , choices =
                [ 'no'
                , 'yes'
                ]
              , full_name = 'lifetime.alive'
              , id = 'lifetime__alive'
              , name = 'alive'
              , sig_key = 1
              , ui_name = 'Lifetime/Alive'
              )
          ]
        , full_name = 'lifetime'
        , id = 'lifetime'
        , name = '-lifetime'
        , sign = '-'
        , ui_name = '-Lifetime'
        )
    , Record
        ( attr = String `last_name`
        , full_name = 'last_name'
        , id = 'last_name'
        , name = 'last_name'
        , sig_key = 3
        , sign = ''
        , ui_name = 'Last name'
        )
    )

    >>> print (qo.order_by_q)
    <Sorted_By: Descending-Getter function for `.lifetime.start`, Descending-Getter function for `.lifetime.finish`, Getter function for `.last_name`>

    >>> AS  = MOM.Attr.Selector
    >>> BiR = SRM.Boat_in_Regatta.E_Type
    >>> fns = AS.List (AS.primary, AS.Name ("points", "place")) (BiR).names
    >>> qrs = QRS (BiR, fns)

    >>> print (formatted (qrs.As_Json_Cargo)) ### SRM.Boat_in_Regatta
    { 'filters' :
        [ { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'name' : 'name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Name'
                      }
                    ]
                , 'name' : 'left'
                , 'sig_key' : 2
                , 'ui_name' : 'Class'
                }
              , { 'name' : 'sail_number'
                , 'sig_key' : 4
                , 'ui_name' : 'Sail number'
                }
              , { 'name' : 'nation'
                , 'sig_key' : 0
                , 'ui_name' : 'Nation'
                }
              , { 'name' : 'sail_number_x'
                , 'sig_key' : 3
                , 'ui_name' : 'Sail number x'
                }
              ]
          , 'name' : 'left'
          , 'sig_key' : 2
          , 'ui_name' : 'Boat'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'name' : 'name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Name'
                      }
                    , { 'attrs' :
                          [ { 'name' : 'start'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Start'
                            }
                          , { 'name' : 'finish'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Finish'
                            }
                          ]
                      , 'name' : 'date'
                      , 'ui_name' : 'Date'
                      }
                    ]
                , 'name' : 'left'
                , 'sig_key' : 2
                , 'ui_name' : 'Event'
                }
              , { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'name' : 'name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Name'
                      }
                    ]
                , 'name' : 'boat_class'
                , 'sig_key' : 2
                , 'ui_name' : 'Boat class'
                }
              ]
          , 'name' : 'right'
          , 'sig_key' : 2
          , 'ui_name' : 'Regatta'
          }
        , { 'name' : 'place'
          , 'sig_key' : 0
          , 'ui_name' : 'Place'
          }
        , { 'name' : 'points'
          , 'sig_key' : 0
          , 'ui_name' : 'Points'
          }
        ]
    , 'name_sep' : '__'
    , 'op_map' :
        { 'CONTAINS' :
            { 'desc' : 'Select entities where the attribute contains the specified value'
            , 'label' : 'contains'
            , 'sym' : 'contains'
            }
        , 'ENDSWITH' :
            { 'desc' : 'Select entities where the attribute value ends with the specified value'
            , 'label' : 'ends-with'
            , 'sym' : 'ends-with'
            }
        , 'EQ' :
            { 'desc' : 'Select entities where the attribute is equal to the specified value'
            , 'label' : '&equiv;'
            , 'sym' : '=='
            }
        , 'EQS' :
            { 'desc' : 'Select entities where the attribute is equal to the specified string value'
            , 'label' : 'EQS'
            , 'sym' : 'EQS'
            }
        , 'GE' :
            { 'desc' : 'Select entities where the attribute is greater than, or equal to, the specified value'
            , 'label' : '&ge;'
            , 'sym' : '>='
            }
        , 'GT' :
            { 'desc' : 'Select entities where the attribute is greater than the specified value'
            , 'label' : '&gt;'
            , 'sym' : '>'
            }
        , 'IN' :
            { 'desc' : 'Select entities where the attribute is a member of the specified list of values'
            , 'label' : 'in'
            , 'sym' : 'in'
            }
        , 'LE' :
            { 'desc' : 'Select entities where the attribute is less than, or equal to, the specified value'
            , 'label' : '&le;'
            , 'sym' : '<='
            }
        , 'LT' :
            { 'desc' : 'Select entities where the attribute is less than the specified value'
            , 'label' : '&lt;'
            , 'sym' : '<'
            }
        , 'NE' :
            { 'desc' : 'Select entities where the attribute is not equal to the specified value'
            , 'label' : '&ne;'
            , 'sym' : '!='
            }
        , 'NES' :
            { 'desc' : 'Select entities where the attribute is not equal to the specified string value'
            , 'label' : 'NES'
            , 'sym' : 'NES'
              }
        , 'STARTSWITH' :
            { 'desc' : 'Select entities where the attribute value starts with the specified value'
            , 'label' : 'starts-with'
            , 'sym' : 'starts-with'
            }
        }
    , 'op_sep' : '___'
    , 'sig_map' :
        { 0 :
            ( 'EQ'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            )
        , 2 :
            ( 'EQ'
            , 'IN'
            , 'NE'
            )
        , 3 :
            ( 'CONTAINS'
            , 'ENDSWITH'
            , 'EQ'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            , 'STARTSWITH'
            )
        , 4 :
            ( 'CONTAINS'
            , 'ENDSWITH'
            , 'EQ'
            , 'EQS'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            , 'NES'
            , 'STARTSWITH'
            )
        }
    , 'ui_sep' : '/'
    }

    >>> def show_f (f, indent = "") :
    ...     print ("%%s%%s" %% (indent, f), f._outer)
    ...     for c in f.Attrs :
    ...         show_f (c, indent + "    ")

    >>> for f in qrs.Attrs :
    ...     show_f (f)
    <left.AQ [Attr.Type.Querier Id_Entity]> <SRM.Boat_in_Regatta.AQ>
        <left.left.AQ [Attr.Type.Querier Id_Entity]> <left.AQ [Attr.Type.Querier Id_Entity]>
            <left.left.name.AQ [Attr.Type.Querier String]> <left.left.AQ [Attr.Type.Querier Id_Entity]>
        <left.sail_number.AQ [Attr.Type.Querier Raw]> <left.AQ [Attr.Type.Querier Id_Entity]>
        <left.nation.AQ [Attr.Type.Querier Ckd]> <left.AQ [Attr.Type.Querier Id_Entity]>
        <left.sail_number_x.AQ [Attr.Type.Querier String]> <left.AQ [Attr.Type.Querier Id_Entity]>
    <right.AQ [Attr.Type.Querier Id_Entity]> <SRM.Boat_in_Regatta.AQ>
        <right.left.AQ [Attr.Type.Querier Id_Entity]> <right.AQ [Attr.Type.Querier Id_Entity]>
            <right.left.name.AQ [Attr.Type.Querier String]> <right.left.AQ [Attr.Type.Querier Id_Entity]>
            <right.left.date.AQ [Attr.Type.Querier Composite]> <right.left.AQ [Attr.Type.Querier Id_Entity]>
                <right.left.date.start.AQ [Attr.Type.Querier Date]> <right.left.date.AQ [Attr.Type.Querier Composite]>
                <right.left.date.finish.AQ [Attr.Type.Querier Date]> <right.left.date.AQ [Attr.Type.Querier Composite]>
        <right.boat_class.AQ [Attr.Type.Querier Id_Entity]> <right.AQ [Attr.Type.Querier Id_Entity]>
            <right.boat_class.name.AQ [Attr.Type.Querier String]> <right.boat_class.AQ [Attr.Type.Querier Id_Entity]>
    <place.AQ [Attr.Type.Querier Ckd]> <SRM.Boat_in_Regatta.AQ>
    <points.AQ [Attr.Type.Querier Ckd]> <SRM.Boat_in_Regatta.AQ>

    >>> print (formatted (list (f.As_Template_Elem for f in qrs.Attrs)))
    [ Record
        ( Class = 'Entity'
        , attr = Boat `left`
        , attrs =
          [ Record
              ( Class = 'Entity'
              , attr = Boat_Class `left`
              , attrs =
                [ Record
                    ( attr = String `name`
                    , full_name = 'left.left.name'
                    , id = 'left__left__name'
                    , name = 'name'
                    , sig_key = 3
                    , ui_name = 'Boat/Class/Name'
                    )
                ]
              , full_name = 'left.left'
              , id = 'left__left'
              , name = 'left'
              , sig_key = 2
              , type_name = 'SRM.Boat_Class'
              , ui_name = 'Boat/Class'
              , ui_type_name = 'Boat_Class'
              )
          , Record
              ( attr = Int `sail_number`
              , full_name = 'left.sail_number'
              , id = 'left__sail_number'
              , name = 'sail_number'
              , sig_key = 4
              , ui_name = 'Boat/Sail number'
              )
          , Record
              ( attr = Nation `nation`
              , choices =
                [ ( 'AUS'
                  , 'Australia'
                  )
                , ( 'AUT'
                  , 'Austria'
                  )
                , ( 'BEL'
                  , 'Belgium'
                  )
                , ( 'CAN'
                  , 'Canada'
                  )
                , ( 'CRO'
                  , 'Croatia'
                  )
                , ( 'CYP'
                  , 'Cyprus'
                  )
                , ( 'CZE'
                  , 'Czech Republic'
                  )
                , ( 'DEN'
                  , 'Denmark'
                  )
                , ( 'ESP'
                  , 'Spain'
                  )
                , ( 'EST'
                  , 'Estonia'
                  )
                , ( 'FIN'
                  , 'Finland'
                  )
                , ( 'FRA'
                  , 'France'
                  )
                , ( 'GBR'
                  , 'Great Britain'
                  )
                , ( 'GER'
                  , 'Germany'
                  )
                , ( 'GRE'
                  , 'Greece'
                  )
                , ( 'HUN'
                  , 'Hungary'
                  )
                , ( 'IRL'
                  , 'Ireland'
                  )
                , ( 'ISL'
                  , 'Iceland'
                  )
                , ( 'ITA'
                  , 'Italy'
                  )
                , ( 'LAT'
                  , 'Latvia'
                  )
                , ( 'LIE'
                  , 'Lichtenstein'
                  )
                , ( 'LTU'
                  , 'Lithuania'
                  )
                , ( 'LUX'
                  , 'Luxembourg'
                  )
                , ( 'MLT'
                  , 'Malta'
                  )
                , ( 'MNE'
                  , 'Montenegro'
                  )
                , ( 'MON'
                  , 'Monaco'
                  )
                , ( 'NED'
                  , 'Netherlands'
                  )
                , ( 'NOR'
                  , 'Norway'
                  )
                , ( 'NZL'
                  , 'New Zealand'
                  )
                , ( 'POL'
                  , 'Poland'
                  )
                , ( 'POR'
                  , 'Portugal'
                  )
                , ( 'ROU'
                  , 'Romania'
                  )
                , ( 'RSA'
                  , 'South Africa'
                  )
                , ( 'RUS'
                  , 'Russia'
                  )
                , ( 'SLO'
                  , 'Slovenia'
                  )
                , ( 'SRB'
                  , 'Serbia'
                  )
                , ( 'SUI'
                  , 'Switzerland'
                  )
                , ( 'SVK'
                  , 'Slovakia'
                  )
                , ( 'SWE'
                  , 'Sweden'
                  )
                , ( 'UKR'
                  , 'Ukraine'
                  )
                , ( 'USA'
                  , 'United States'
                  )
                ]
              , full_name = 'left.nation'
              , id = 'left__nation'
              , name = 'nation'
              , sig_key = 0
              , ui_name = 'Boat/Nation'
              )
          , Record
              ( attr = String `sail_number_x`
              , full_name = 'left.sail_number_x'
              , id = 'left__sail_number_x'
              , name = 'sail_number_x'
              , sig_key = 3
              , ui_name = 'Boat/Sail number x'
              )
          ]
        , full_name = 'left'
        , id = 'left'
        , name = 'left'
        , sig_key = 2
        , type_name = 'SRM.Boat'
        , ui_name = 'Boat'
        , ui_type_name = 'Boat'
        )
    , Record
        ( Class = 'Entity'
        , attr = Regatta `right`
        , attrs =
          [ Record
              ( Class = 'Entity'
              , attr = Regatta_Event `left`
              , attrs =
                [ Record
                    ( attr = String `name`
                    , full_name = 'right.left.name'
                    , id = 'right__left__name'
                    , name = 'name'
                    , sig_key = 3
                    , ui_name = 'Regatta/Event/Name'
                    )
                , Record
                    ( attr = Date_Interval `date`
                    , attrs =
                      [ Record
                          ( attr = Date `start`
                          , full_name = 'right.left.date.start'
                          , id = 'right__left__date__start'
                          , name = 'start'
                          , sig_key = 0
                          , ui_name = 'Regatta/Event/Date/Start'
                          )
                      , Record
                          ( attr = Date `finish`
                          , full_name = 'right.left.date.finish'
                          , id = 'right__left__date__finish'
                          , name = 'finish'
                          , sig_key = 0
                          , ui_name = 'Regatta/Event/Date/Finish'
                          )
                      ]
                    , full_name = 'right.left.date'
                    , id = 'right__left__date'
                    , name = 'date'
                    , ui_name = 'Regatta/Event/Date'
                    )
                ]
              , full_name = 'right.left'
              , id = 'right__left'
              , name = 'left'
              , sig_key = 2
              , type_name = 'SRM.Regatta_Event'
              , ui_name = 'Regatta/Event'
              , ui_type_name = 'Regatta_Event'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `boat_class`
              , attrs =
                [ Record
                    ( attr = String `name`
                    , full_name = 'right.boat_class.name'
                    , id = 'right__boat_class__name'
                    , name = 'name'
                    , sig_key = 3
                    , ui_name = 'Regatta/Boat class/Name'
                    )
                ]
              , full_name = 'right.boat_class'
              , id = 'right__boat_class'
              , name = 'boat_class'
              , sig_key = 2
              , type_name = 'SRM._Boat_Class_'
              , ui_name = 'Regatta/Boat class'
              , ui_type_name = '_Boat_Class_'
              )
          ]
        , full_name = 'right'
        , id = 'right'
        , name = 'right'
        , sig_key = 2
        , type_name = 'SRM.Regatta'
        , ui_name = 'Regatta'
        , ui_type_name = 'Regatta'
        )
    , Record
        ( attr = Int `place`
        , full_name = 'place'
        , id = 'place'
        , name = 'place'
        , sig_key = 0
        , ui_name = 'Place'
        )
    , Record
        ( attr = Int `points`
        , full_name = 'points'
        , id = 'points'
        , name = 'points'
        , sig_key = 0
        , ui_name = 'Points'
        )
    ]

    >>> AS  = MOM.Attr.Selector
    >>> fns = AS.ui_attr (PAP.Person.E_Type).names
    >>> qrs = QRS (PAP.Person.E_Type, fns)

    >>> print (formatted (qrs.As_Json_Cargo)) ### PAP.Person
    { 'filters' :
        [ { 'name' : 'last_name'
          , 'sig_key' : 3
          , 'ui_name' : 'Last name'
          }
        , { 'name' : 'first_name'
          , 'sig_key' : 3
          , 'ui_name' : 'First name'
          }
        , { 'name' : 'middle_name'
          , 'sig_key' : 3
          , 'ui_name' : 'Middle name'
          }
        , { 'name' : 'title'
          , 'sig_key' : 3
          , 'ui_name' : 'Academic title'
          }
        , { 'attrs' :
              [ { 'name' : 'start'
                , 'sig_key' : 0
                , 'ui_name' : 'Start'
                }
              , { 'name' : 'finish'
                , 'sig_key' : 0
                , 'ui_name' : 'Finish'
                }
              ]
          , 'name' : 'lifetime'
          , 'ui_name' : 'Lifetime'
          }
        , { 'name' : 'sex'
          , 'sig_key' : 0
          , 'ui_name' : 'Sex'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'c_time'
                , 'sig_key' : 0
                , 'ui_name' : 'C time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'c_user'
                , 'sig_key' : 2
                , 'ui_name' : 'C user'
                }
              , { 'name' : 'kind'
                , 'sig_key' : 3
                , 'ui_name' : 'Kind'
                }
              , { 'name' : 'time'
                , 'sig_key' : 0
                , 'ui_name' : 'Time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'user'
                , 'sig_key' : 2
                , 'ui_name' : 'User'
                }
              ]
          , 'name' : 'creation'
          , 'sig_key' : 2
          , 'ui_name' : 'Creation'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'c_time'
                , 'sig_key' : 0
                , 'ui_name' : 'C time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'c_user'
                , 'sig_key' : 2
                , 'ui_name' : 'C user'
                }
              , { 'name' : 'kind'
                , 'sig_key' : 3
                , 'ui_name' : 'Kind'
                }
              , { 'name' : 'time'
                , 'sig_key' : 0
                , 'ui_name' : 'Time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'user'
                , 'sig_key' : 2
                , 'ui_name' : 'User'
                }
              ]
          , 'name' : 'last_change'
          , 'sig_key' : 2
          , 'ui_name' : 'Last change'
          }
        , { 'name' : 'last_cid'
          , 'sig_key' : 0
          , 'ui_name' : 'Last cid'
          }
        , { 'name' : 'pid'
          , 'sig_key' : 0
          , 'ui_name' : 'Pid'
          }
        , { 'name' : 'type_name'
          , 'sig_key' : 3
          , 'ui_name' : 'Type name'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'attrs' :
                    [ { 'attrs' :
                          [ { 'name' : 'day'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Day'
                            }
                          , { 'name' : 'month'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Month'
                            }
                          , { 'name' : 'year'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Year'
                            }
                          ]
                      , 'name' : 'start'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Start'
                      }
                    , { 'attrs' :
                          [ { 'name' : 'day'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Day'
                            }
                          , { 'name' : 'month'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Month'
                            }
                          , { 'name' : 'year'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Year'
                            }
                          ]
                      , 'name' : 'finish'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Finish'
                      }
                    , { 'name' : 'alive'
                      , 'sig_key' : 1
                      , 'ui_name' : 'Alive'
                      }
                    ]
                , 'name' : 'date'
                , 'ui_name' : 'Date'
                }
              , { 'attrs' :
                    [ { 'attrs' :
                          [ { 'name' : 'hour'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Hour'
                            }
                          , { 'name' : 'minute'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Minute'
                            }
                          , { 'name' : 'second'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Second'
                            }
                          ]
                      , 'name' : 'start'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Start'
                      }
                    , { 'attrs' :
                          [ { 'name' : 'hour'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Hour'
                            }
                          , { 'name' : 'minute'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Minute'
                            }
                          , { 'name' : 'second'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Second'
                            }
                          ]
                      , 'name' : 'finish'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Finish'
                      }
                    ]
                , 'name' : 'time'
                , 'ui_name' : 'Time'
                }
              , { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'name' : 'name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Name'
                      }
                    , { 'name' : 'desc'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Description'
                      }
                    ]
                , 'name' : 'calendar'
                , 'sig_key' : 2
                , 'ui_name' : 'Calendar'
                }
              , { 'name' : 'detail'
                , 'sig_key' : 3
                , 'ui_name' : 'Detail'
                }
              , { 'name' : 'short_title'
                , 'sig_key' : 3
                , 'ui_name' : 'Short title'
                }
              ]
          , 'name' : 'events'
          , 'sig_key' : 2
          , 'ui_name' : 'Events'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'name'
                , 'sig_key' : 3
                , 'ui_name' : 'Name'
                }
              , { 'name' : 'enabled'
                , 'sig_key' : 1
                , 'ui_name' : 'Enabled'
                }
              , { 'name' : 'superuser'
                , 'sig_key' : 1
                , 'ui_name' : 'Superuser'
                }
              , { 'name' : 'active'
                , 'sig_key' : 1
                , 'ui_name' : 'Active'
                }
              , { 'name' : 'suspended'
                , 'sig_key' : 1
                , 'ui_name' : 'Suspended'
                }
              ]
          , 'name' : 'accounts'
          , 'sig_key' : 2
          , 'ui_name' : 'Accounts'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'mna_number'
                , 'sig_key' : 4
                , 'ui_name' : 'Mna number'
                }
              , { 'name' : 'nation'
                , 'sig_key' : 0
                , 'ui_name' : 'Nation'
                }
              , { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'name' : 'name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Name'
                      }
                    , { 'name' : 'long_name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Long name'
                      }
                    ]
                , 'name' : 'club'
                , 'sig_key' : 2
                , 'ui_name' : 'Club'
                }
              ]
          , 'name' : 'sailors'
          , 'sig_key' : 2
          , 'ui_name' : 'Sailors'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'value'
                , 'sig_key' : 3
                , 'ui_name' : 'Value'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              ]
          , 'name' : 'urls'
          , 'sig_key' : 2
          , 'ui_name' : 'Urls'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'sn'
                , 'sig_key' : 3
                , 'ui_name' : 'Subscriber number'
                }
              , { 'name' : 'ndc'
                , 'sig_key' : 3
                , 'ui_name' : 'Network destination code'
                }
              , { 'name' : 'cc'
                , 'sig_key' : 3
                , 'ui_name' : 'Country code'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              ]
          , 'name' : 'phones'
          , 'sig_key' : 2
          , 'ui_name' : 'Phones'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'address'
                , 'sig_key' : 3
                , 'ui_name' : 'Email address'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              ]
          , 'name' : 'emails'
          , 'sig_key' : 2
          , 'ui_name' : 'Emails'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'street'
                , 'sig_key' : 3
                , 'ui_name' : 'Street'
                }
              , { 'name' : 'zip'
                , 'sig_key' : 3
                , 'ui_name' : 'Zip code'
                }
              , { 'name' : 'city'
                , 'sig_key' : 3
                , 'ui_name' : 'City'
                }
              , { 'name' : 'country'
                , 'sig_key' : 3
                , 'ui_name' : 'Country'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              , { 'name' : 'region'
                , 'sig_key' : 3
                , 'ui_name' : 'Region'
                }
              ]
          , 'name' : 'addresses'
          , 'sig_key' : 2
          , 'ui_name' : 'Addresses'
          }
        ]
    , 'name_sep' : '__'
    , 'op_map' :
        { 'CONTAINS' :
            { 'desc' : 'Select entities where the attribute contains the specified value'
            , 'label' : 'contains'
            , 'sym' : 'contains'
            }
        , 'ENDSWITH' :
            { 'desc' : 'Select entities where the attribute value ends with the specified value'
            , 'label' : 'ends-with'
            , 'sym' : 'ends-with'
            }
        , 'EQ' :
            { 'desc' : 'Select entities where the attribute is equal to the specified value'
            , 'label' : '&equiv;'
            , 'sym' : '=='
            }
        , 'EQS' :
            { 'desc' : 'Select entities where the attribute is equal to the specified string value'
            , 'label' : 'EQS'
            , 'sym' : 'EQS'
            }
        , 'GE' :
            { 'desc' : 'Select entities where the attribute is greater than, or equal to, the specified value'
            , 'label' : '&ge;'
            , 'sym' : '>='
            }
        , 'GT' :
            { 'desc' : 'Select entities where the attribute is greater than the specified value'
            , 'label' : '&gt;'
            , 'sym' : '>'
            }
        , 'IN' :
            { 'desc' : 'Select entities where the attribute is a member of the specified list of values'
            , 'label' : 'in'
            , 'sym' : 'in'
            }
        , 'LE' :
            { 'desc' : 'Select entities where the attribute is less than, or equal to, the specified value'
            , 'label' : '&le;'
            , 'sym' : '<='
            }
        , 'LT' :
            { 'desc' : 'Select entities where the attribute is less than the specified value'
            , 'label' : '&lt;'
            , 'sym' : '<'
            }
        , 'NE' :
            { 'desc' : 'Select entities where the attribute is not equal to the specified value'
            , 'label' : '&ne;'
            , 'sym' : '!='
            }
        , 'NES' :
            { 'desc' : 'Select entities where the attribute is not equal to the specified string value'
            , 'label' : 'NES'
            , 'sym' : 'NES'
            }
        , 'STARTSWITH' :
            { 'desc' : 'Select entities where the attribute value starts with the specified value'
            , 'label' : 'starts-with'
            , 'sym' : 'starts-with'
            }
        }
    , 'op_sep' : '___'
    , 'sig_map' :
        { 0 :
            ( 'EQ'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            )
        , 1 : ('EQ', )
        , 2 :
            ( 'EQ'
            , 'IN'
            , 'NE'
            )
        , 3 :
            ( 'CONTAINS'
            , 'ENDSWITH'
            , 'EQ'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            , 'STARTSWITH'
            )
        , 4 :
            ( 'CONTAINS'
            , 'ENDSWITH'
            , 'EQ'
            , 'EQS'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            , 'NES'
            , 'STARTSWITH'
            )
        }
    , 'ui_sep' : '/'
    }

"""

_test_pepk = """
    >>> root  = Scaffold (["wsgi", "-db_url", %(p1)s, "-db_name", %(n1)s or ("test." + %(bn1)s)]) # doctest:+ELLIPSIS
    >>> scope = root.scope
    >>> PAP   = scope.PAP

    >>> rd = f_req (last_name = "Qux")
    >>> for afa in QR.af_args_fif (rd.req_data, QR._a_pat_opt) :
    ...    prepr (afa)
    ('last_name___EQ', 'last_name', '', '', 'EQ', 'Qux')

    >>> print (formatted (QR.Filter (PAP.Person.E_Type, "last_name", "Qux")))
    Record
    ( AQ = <last_name.AQ [Attr.Type.Querier String_FL]>
    , attr = String `last_name`
    , edit = 'Qux'
    , full_name = 'last_name'
    , id = 'last_name___AC'
    , name = 'last_name___AC'
    , op = Record
        ( desc = 'Select entities where the attribute value starts with the specified value'
        , label = 'auto-complete'
        )
    , sig_key = 3
    , ui_name = 'Last name'
    , value = 'Qux'
    )

    >>> rdd = \\
    ...   { "spouse[PAP.Person]__last_name___GE" : "Qux"
    ...   , "spouse[PAP.Person]__lifetime__start___EQ" : "2008"
    ...   , "title___EQ" : "Dr."
    ...   , "foo" : "bar"
    ...   }
    >>> rdx = f_req (** rdd)

    >>> for afa in QR.af_args_fif (rdx.req_data) :
    ...    prepr (afa)
    ('spouse[PAP.Person]__last_name___GE', 'spouse', 'PAP.Person', 'last_name', 'GE', 'Qux')
    ('spouse[PAP.Person]__lifetime__start___EQ', 'spouse', 'PAP.Person', 'lifetime.start', 'EQ', '2008')
    ('title___EQ', 'title', '', '', 'EQ', 'Dr.')

    >>> qrx = QR.from_request (scope, PAP.Person_M.E_Type, rdx)
    >>> print (formatted (qrx.filters))
    ( Record
        ( AQ = <title.AQ [Attr.Type.Querier String]>
        , attr = String `title`
        , edit = 'Dr.'
        , full_name = 'title'
        , id = 'title___EQ'
        , name = 'title___EQ'
        , op =
          Record
            ( desc = 'Select entities where the attribute is equal to the specified value'
            , label = '&equiv;'
            )
        , sig_key = 3
        , ui_name = 'Academic title'
        , value = 'Dr.'
        )
    , Record
        ( AQ = <last_name.AQ [Attr.Type.Querier String_FL]>
        , attr = String `last_name`
        , edit = 'Qux'
        , full_name = 'spouse[PAP.Person].last_name'
        , id = 'spouse[PAP.Person]__last_name___GE'
        , name = 'spouse[PAP.Person]__last_name___GE'
        , op =
          Record
            ( desc = 'Select entities where the attribute is greater than, or equal to, the specified value'
            , label = '&ge;'
            )
        , sig_key = 3
        , ui_name = 'Spouse/Last name'
        , value = 'Qux'
        )
    , Record
        ( AQ = <lifetime.start.AQ [Attr.Type.Querier Date]>
        , attr = Date `start`
        , attrs =
          [ Record
              ( attr = Int `day`
              , full_name = 'lifetime.start.day'
              , id = 'lifetime__start__day'
              , name = 'day'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Day'
              )
          , Record
              ( attr = Int `month`
              , full_name = 'lifetime.start.month'
              , id = 'lifetime__start__month'
              , name = 'month'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Month'
              )
          , Record
              ( attr = Int `year`
              , full_name = 'lifetime.start.year'
              , id = 'lifetime__start__year'
              , name = 'year'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Year'
              )
          ]
        , edit = '2008'
        , full_name = 'spouse[PAP.Person].lifetime.start'
        , id = 'spouse[PAP.Person]__lifetime__start___EQ'
        , name = 'spouse[PAP.Person]__lifetime__start___EQ'
        , op =
          Record
            ( desc = 'Select entities where the attribute is equal to the specified value'
            , label = '&equiv;'
            )
        , sig_key = 0
        , ui_name = 'Spouse/Lifetime/Start'
        , value = '2008'
        )
    )

    >>> p1  = PAP.Person_M ("Qux", "Foo", lifetime = ("20080327",), raw = True)
    >>> p2  = PAP.Person_M ("Bar", "Baz", title = "Dr.", spouse = p1, raw = True)

    >>> PAP.Person_M.query (sort_key = TFL.Sorted_By ("pid")).all ()
    [PAP.Person_M ('qux', 'foo', '', ''), PAP.Person_M ('bar', 'baz', '', 'dr.')]
    >>> pids = PAP.Person_M.query (sort_key = TFL.Sorted_By ("pid")).attr ("pid").all ()
    >>> list (int (p) for p in pids)
    [1, 2]

    >>> p1.pid, p1 in pids, p1 in [1, 2], p1 == p1.pid, p1.pid == p1
    (1, True, True, True, True)
    >>> p2.pid, p2 in pids, p2 in [1, 2], p2 == p2.pid, p2.pid == p2
    (2, True, True, True, True)
    >>> p1.spouse and p1.spouse.pid, p1.spouse in [1]
    (None, False)
    >>> p2.spouse and p2.spouse.pid, p2.spouse in [1], p2.spouse == p1.pid, p1.pid == p2.spouse
    (1, True, True, True)

    >>> req = Scaffold.test_request_get ("/Admin/Person?spouse[PAP.Person]__last_name___GE=Qux&spouse[PAP.Person]__lifetime__start___EQ=2008&title___EQ=Dr.")
    >>> qr  = QR.from_request (scope, PAP.Person_M.E_Type, req)
    >>> print (formatted (qr.filters))
    ( Record
        ( AQ = <title.AQ [Attr.Type.Querier String]>
        , attr = String `title`
        , edit = 'Dr.'
        , full_name = 'title'
        , id = 'title___EQ'
        , name = 'title___EQ'
        , op =
          Record
            ( desc = 'Select entities where the attribute is equal to the specified value'
            , label = '&equiv;'
            )
        , sig_key = 3
        , ui_name = 'Academic title'
        , value = 'Dr.'
        )
    , Record
        ( AQ = <last_name.AQ [Attr.Type.Querier String_FL]>
        , attr = String `last_name`
        , edit = 'Qux'
        , full_name = 'spouse[PAP.Person].last_name'
        , id = 'spouse[PAP.Person]__last_name___GE'
        , name = 'spouse[PAP.Person]__last_name___GE'
        , op =
          Record
            ( desc = 'Select entities where the attribute is greater than, or equal to, the specified value'
            , label = '&ge;'
            )
        , sig_key = 3
        , ui_name = 'Spouse/Last name'
        , value = 'Qux'
        )
    , Record
        ( AQ = <lifetime.start.AQ [Attr.Type.Querier Date]>
        , attr = Date `start`
        , attrs =
          [ Record
              ( attr = Int `day`
              , full_name = 'lifetime.start.day'
              , id = 'lifetime__start__day'
              , name = 'day'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Day'
              )
          , Record
              ( attr = Int `month`
              , full_name = 'lifetime.start.month'
              , id = 'lifetime__start__month'
              , name = 'month'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Month'
              )
          , Record
              ( attr = Int `year`
              , full_name = 'lifetime.start.year'
              , id = 'lifetime__start__year'
              , name = 'year'
              , sig_key = 0
              , ui_name = 'Lifetime/Start/Year'
              )
          ]
        , edit = '2008'
        , full_name = 'spouse[PAP.Person].lifetime.start'
        , id = 'spouse[PAP.Person]__lifetime__start___EQ'
        , name = 'spouse[PAP.Person]__lifetime__start___EQ'
        , op =
          Record
            ( desc = 'Select entities where the attribute is equal to the specified value'
            , label = '&equiv;'
            )
        , sig_key = 0
        , ui_name = 'Spouse/Lifetime/Start'
        , value = '2008'
        )
    )


    >>> list (int (p) for p in PAP.Person_M.query (sort_key = TFL.Sorted_By ("pid")).attr ("pid"))
    [1, 2]

    >>> list (int (p) for p in PAP.Person_M.query (* qr.filters_q, sort_key = TFL.Sorted_By ("pid")).attr ("pid"))
    [2]

    >>> qr (PAP.Person_M.query (sort_key = TFL.Sorted_By ("pid"))).all ()
    [PAP.Person_M ('bar', 'baz', '', 'dr.')]

    >>> print (formatted (PAP.Subject_has_Property.AQ.As_Json_Cargo ["filters"]))
    [ { 'Class' : 'Entity'
      , 'children_np' :
          [ { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Association'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Association'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                , { 'name' : 'registered_in'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Registered in'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Company'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Company'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'last_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Last name'
                  }
                , { 'name' : 'first_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'First name'
                  }
                , { 'name' : 'middle_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Middle name'
                  }
                , { 'name' : 'title'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Academic title'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Person'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Person'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'last_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Last name'
                  }
                , { 'name' : 'first_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'First name'
                  }
                , { 'name' : 'middle_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Middle name'
                  }
                , { 'name' : 'title'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Academic title'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Person_M'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Person_M'
            }
          ]
      , 'default_child' : 'PAP.Person'
      , 'name' : 'left'
      , 'sig_key' : 2
      , 'ui_name' : 'Subject'
      }
    , { 'Class' : 'Entity'
      , 'children_np' :
          [ { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'street'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Street'
                  }
                , { 'name' : 'zip'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Zip code'
                  }
                , { 'name' : 'city'
                  , 'sig_key' : 3
                  , 'ui_name' : 'City'
                  }
                , { 'name' : 'country'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Country'
                  }
                ]
            , 'name' : 'right'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Address'
            , 'ui_name' : 'Property'
            , 'ui_type_name' : 'Address'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'address'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Email address'
                  }
                ]
            , 'name' : 'right'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Email'
            , 'ui_name' : 'Property'
            , 'ui_type_name' : 'Email'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'sn'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Subscriber number'
                  }
                , { 'name' : 'ndc'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Network destination code'
                  }
                , { 'name' : 'cc'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Country code'
                  }
                ]
            , 'name' : 'right'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Phone'
            , 'ui_name' : 'Property'
            , 'ui_type_name' : 'Phone'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'value'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Value'
                  }
                ]
            , 'name' : 'right'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Url'
            , 'ui_name' : 'Property'
            , 'ui_type_name' : 'Url'
            }
          ]
      , 'name' : 'right'
      , 'sig_key' : 2
      , 'ui_name' : 'Property'
      }
    , { 'name' : 'desc'
      , 'sig_key' : 3
      , 'ui_name' : 'Description'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'c_time'
            , 'sig_key' : 0
            , 'ui_name' : 'C time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'c_user'
            , 'sig_key' : 2
            , 'ui_name' : 'C user'
            }
          , { 'name' : 'kind'
            , 'sig_key' : 3
            , 'ui_name' : 'Kind'
            }
          , { 'name' : 'time'
            , 'sig_key' : 0
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'user'
            , 'sig_key' : 2
            , 'ui_name' : 'User'
            }
          ]
      , 'name' : 'creation'
      , 'sig_key' : 2
      , 'ui_name' : 'Creation'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'c_time'
            , 'sig_key' : 0
            , 'ui_name' : 'C time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'c_user'
            , 'sig_key' : 2
            , 'ui_name' : 'C user'
            }
          , { 'name' : 'kind'
            , 'sig_key' : 3
            , 'ui_name' : 'Kind'
            }
          , { 'name' : 'time'
            , 'sig_key' : 0
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'user'
            , 'sig_key' : 2
            , 'ui_name' : 'User'
            }
          ]
      , 'name' : 'last_change'
      , 'sig_key' : 2
      , 'ui_name' : 'Last change'
      }
    , { 'name' : 'last_cid'
      , 'sig_key' : 0
      , 'ui_name' : 'Last cid'
      }
    , { 'name' : 'pid'
      , 'sig_key' : 0
      , 'ui_name' : 'Pid'
      }
    , { 'name' : 'type_name'
      , 'sig_key' : 3
      , 'ui_name' : 'Type name'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'attrs' :
                [ { 'attrs' :
                      [ { 'name' : 'day'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Day'
                        }
                      , { 'name' : 'month'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Month'
                        }
                      , { 'name' : 'year'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Year'
                        }
                      ]
                  , 'name' : 'start'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Start'
                  }
                , { 'attrs' :
                      [ { 'name' : 'day'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Day'
                        }
                      , { 'name' : 'month'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Month'
                        }
                      , { 'name' : 'year'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Year'
                        }
                      ]
                  , 'name' : 'finish'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Finish'
                  }
                , { 'name' : 'alive'
                  , 'sig_key' : 1
                  , 'ui_name' : 'Alive'
                  }
                ]
            , 'name' : 'date'
            , 'ui_name' : 'Date'
            }
          , { 'attrs' :
                [ { 'attrs' :
                      [ { 'name' : 'hour'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Hour'
                        }
                      , { 'name' : 'minute'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Minute'
                        }
                      , { 'name' : 'second'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Second'
                        }
                      ]
                  , 'name' : 'start'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Start'
                  }
                , { 'attrs' :
                      [ { 'name' : 'hour'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Hour'
                        }
                      , { 'name' : 'minute'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Minute'
                        }
                      , { 'name' : 'second'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Second'
                        }
                      ]
                  , 'name' : 'finish'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Finish'
                  }
                ]
            , 'name' : 'time'
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                , { 'name' : 'desc'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Description'
                  }
                ]
            , 'name' : 'calendar'
            , 'sig_key' : 2
            , 'ui_name' : 'Calendar'
            }
          , { 'name' : 'detail'
            , 'sig_key' : 3
            , 'ui_name' : 'Detail'
            }
          , { 'name' : 'short_title'
            , 'sig_key' : 3
            , 'ui_name' : 'Short title'
            }
          ]
      , 'name' : 'events'
      , 'sig_key' : 2
      , 'ui_name' : 'Events'
      }
    ]

    >>> print (formatted (PAP.Subject_has_Phone.AQ.As_Json_Cargo ["filters"]))
    [ { 'Class' : 'Entity'
      , 'children_np' :
          [ { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Association'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Association'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                , { 'name' : 'registered_in'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Registered in'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Company'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Company'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'last_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Last name'
                  }
                , { 'name' : 'first_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'First name'
                  }
                , { 'name' : 'middle_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Middle name'
                  }
                , { 'name' : 'title'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Academic title'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Person'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Person'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'last_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Last name'
                  }
                , { 'name' : 'first_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'First name'
                  }
                , { 'name' : 'middle_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Middle name'
                  }
                , { 'name' : 'title'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Academic title'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Person_M'
            , 'ui_name' : 'Subject'
            , 'ui_type_name' : 'Person_M'
            }
          ]
      , 'default_child' : 'PAP.Person'
      , 'name' : 'left'
      , 'sig_key' : 2
      , 'ui_name' : 'Subject'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'sn'
            , 'sig_key' : 3
            , 'ui_name' : 'Subscriber number'
            }
          , { 'name' : 'ndc'
            , 'sig_key' : 3
            , 'ui_name' : 'Network destination code'
            }
          , { 'name' : 'cc'
            , 'sig_key' : 3
            , 'ui_name' : 'Country code'
            }
          , { 'name' : 'desc'
            , 'sig_key' : 3
            , 'ui_name' : 'Description'
            }
          ]
      , 'name' : 'right'
      , 'sig_key' : 2
      , 'ui_name' : 'Phone'
      }
    , { 'name' : 'extension'
      , 'sig_key' : 3
      , 'ui_name' : 'Extension'
      }
    , { 'name' : 'desc'
      , 'sig_key' : 3
      , 'ui_name' : 'Description'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'c_time'
            , 'sig_key' : 0
            , 'ui_name' : 'C time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'c_user'
            , 'sig_key' : 2
            , 'ui_name' : 'C user'
            }
          , { 'name' : 'kind'
            , 'sig_key' : 3
            , 'ui_name' : 'Kind'
            }
          , { 'name' : 'time'
            , 'sig_key' : 0
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'user'
            , 'sig_key' : 2
            , 'ui_name' : 'User'
            }
          ]
      , 'name' : 'creation'
      , 'sig_key' : 2
      , 'ui_name' : 'Creation'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'c_time'
            , 'sig_key' : 0
            , 'ui_name' : 'C time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'c_user'
            , 'sig_key' : 2
            , 'ui_name' : 'C user'
            }
          , { 'name' : 'kind'
            , 'sig_key' : 3
            , 'ui_name' : 'Kind'
            }
          , { 'name' : 'time'
            , 'sig_key' : 0
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'user'
            , 'sig_key' : 2
            , 'ui_name' : 'User'
            }
          ]
      , 'name' : 'last_change'
      , 'sig_key' : 2
      , 'ui_name' : 'Last change'
      }
    , { 'name' : 'last_cid'
      , 'sig_key' : 0
      , 'ui_name' : 'Last cid'
      }
    , { 'name' : 'pid'
      , 'sig_key' : 0
      , 'ui_name' : 'Pid'
      }
    , { 'name' : 'type_name'
      , 'sig_key' : 3
      , 'ui_name' : 'Type name'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'attrs' :
                [ { 'attrs' :
                      [ { 'name' : 'day'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Day'
                        }
                      , { 'name' : 'month'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Month'
                        }
                      , { 'name' : 'year'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Year'
                        }
                      ]
                  , 'name' : 'start'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Start'
                  }
                , { 'attrs' :
                      [ { 'name' : 'day'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Day'
                        }
                      , { 'name' : 'month'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Month'
                        }
                      , { 'name' : 'year'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Year'
                        }
                      ]
                  , 'name' : 'finish'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Finish'
                  }
                , { 'name' : 'alive'
                  , 'sig_key' : 1
                  , 'ui_name' : 'Alive'
                  }
                ]
            , 'name' : 'date'
            , 'ui_name' : 'Date'
            }
          , { 'attrs' :
                [ { 'attrs' :
                      [ { 'name' : 'hour'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Hour'
                        }
                      , { 'name' : 'minute'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Minute'
                        }
                      , { 'name' : 'second'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Second'
                        }
                      ]
                  , 'name' : 'start'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Start'
                  }
                , { 'attrs' :
                      [ { 'name' : 'hour'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Hour'
                        }
                      , { 'name' : 'minute'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Minute'
                        }
                      , { 'name' : 'second'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Second'
                        }
                      ]
                  , 'name' : 'finish'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Finish'
                  }
                ]
            , 'name' : 'time'
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                , { 'name' : 'desc'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Description'
                  }
                ]
            , 'name' : 'calendar'
            , 'sig_key' : 2
            , 'ui_name' : 'Calendar'
            }
          , { 'name' : 'detail'
            , 'sig_key' : 3
            , 'ui_name' : 'Detail'
            }
          , { 'name' : 'short_title'
            , 'sig_key' : 3
            , 'ui_name' : 'Short title'
            }
          ]
      , 'name' : 'events'
      , 'sig_key' : 2
      , 'ui_name' : 'Events'
      }
    ]


"""

_test_filters_q = r"""
    >>> root  = Scaffold (["wsgi", "-db_url", %(p1)s, "-db_name", %(n1)s or ("test." + %(bn1)s)]) # doctest:+ELLIPSIS
    >>> scope = root.scope
    >>> PAP   = scope.PAP

    >>> url = "/Admin/Person?spouse[PAP.Person]__last_name___GE=Qux&spouse[PAP.Person]__lifetime__start___EQ=2008&title___EQ=Dr."
    >>> req = Scaffold.test_request_get (url)
    >>> qr  = QR.from_request (scope, PAP.Person_M.E_Type, req)
    >>> qr.filters_q # doctest:+ELLIPSIS
    (Q.title == 'dr.', Q.spouse.in_ (SQL: SELECT DISTINCT mom_id_entity.pid AS mom_id_entity_pid
         FROM mom_id_entity
           JOIN pap_person ON mom_id_entity.pid = pap_person.pid
           LEFT OUTER JOIN pap_person_m ON pap_person.pid = pap_person_m.pid
         WHERE pap_person.last_name >= :last_name_1
            AND pap_person.lifetime__start IS NOT NULL
            AND pap_person.lifetime__start >= :lifetime__start_1
            AND pap_person.lifetime__start <= :lifetime__start_2,))

"""

from   _GTW.__test__.model                   import *
from   _GTW._RST._TOP._MOM.Query_Restriction import \
     ( Query_Restriction      as QR
     , Query_Restriction_Spec as QRS
     )
import _GTW._OMP._PAP.Association

f_req = fake_request

_Ancestor_Essence = GTW.OMP.PAP.Person

class Person_M (_Ancestor_Essence) :
    """Married person"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class spouse (A_Id_Entity) :
            """Spouse of this person"""

            kind               = Attr.Necessary
            P_Type             = "GTW.OMP.PAP.Subject"

        # end class spouse

    # end class _Attributes

# end class Person_M

from   itertools                             import chain as ichain

__test__ = Scaffold.create_test_dict \
    ( dict
      ( main       = _test_code
      , test_pepk  = _test_pepk
      )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( test_filters_q = _test_filters_q
            )
        , ignore = ("HPS", )
        )
    )


### __END__ GTW.__test__.Query_Restriction
