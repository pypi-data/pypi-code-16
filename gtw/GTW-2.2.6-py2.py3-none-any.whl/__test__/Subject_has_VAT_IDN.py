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
#    GTW.__test__.Subject_has_VAT_IDN
#
# Purpose
#    Test PAP.Subject_has_VAT_IDN
#
# Revision Dates
#    24-Feb-2016 (CT) Creation
#    25-Feb-2016 (CT) Add tests for `Wrong_Type`
#    14-Apr-2016 (CT) Use `expect_except` to support Python 3.x
#    18-May-2016 (CT) Add `test_qr`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> p1  = PAP.Person ("Doe", "Jane", title = "Dr.", raw = True)
    >>> p2  = PAP.Person ("Doe", "John", raw = True)
    >>> c1  = PAP.Company_1P (person = p1, raw = True)
    >>> c2  = PAP.Company ("John Doe, Inc.", "Paris")
    >>> c3  = PAP.Company ("Jane Doe, Inc.", "Paris")

    >>> print (PAP.Company_1P.E_Type.vat_idn.description)
    VAT identification number of Company_1P.

    >>> print (p1.ui_display, ": VAT-IDN =", p1.vat_idn)
    Doe Jane, Dr. : VAT-IDN = None

    >>> print (c1.ui_display, ": VAT-IDN =", c1.vat_idn)
    Doe Jane, Dr. : VAT-IDN = None

    >>> print (c2.ui_display, ": VAT-IDN =", c2.vat_idn)
    John Doe, Inc., Paris : VAT-IDN = None

    >>> eu1 = PAP.Person_has_VAT_IDN  (p1, vin = "GB999 9999 73")

    >>> with expect_except (MOM.Error.Wrong_Type) :
    ...     _ = PAP.Person_has_VAT_IDN  (c3, vin = "GB999 9999 72")
    Wrong_Type: Company 'Jane Doe, Inc., Paris' not eligible for attribute left,
        must be instance of Person

    >>> with expect_except (MOM.Error.Wrong_Type) :
    ...     _ = PAP.Company_has_VAT_IDN (p2, vin = "GB999 9999 72")
    Wrong_Type: Person 'Doe John' not eligible for attribute left,
        must be instance of Company

    >>> with expect_except (MOM.Error.Wrong_Type) :
    ...     _ = PAP.Company_has_VAT_IDN (c1, vin = "GB999 9999 72")
    Wrong_Type: Company_1P 'Doe Jane, Dr.' not eligible for attribute left,
        must be instance of Company, but not Company_1P

    >>> eu2 = PAP.Company_has_VAT_IDN (c2, vin = "FR83,404,833,048")

    >>> eu1
    PAP.Person_has_VAT_IDN (('doe', 'jane', '', 'dr.'), GB999999973)

    >>> eu2
    PAP.Company_has_VAT_IDN (('john doe, inc.', 'paris'), FR83404833048)

    >>> print (eu1.ui_display)
    Doe Jane, Dr., GB999999973

    >>> print (eu2.ui_display)
    John Doe, Inc., Paris, FR83404833048

    >>> with expect_except (MOM.Error.Invariants) :
    ...     _ = PAP.Person_has_VAT_IDN  (p2, vin = "FR83,404,833,048") # doctest:+ELLIPSIS
    Invariants: The attribute values for 'vin' must be unique for each object
      The new definition of Person_has_VAT_IDN PAP.Person_has_VAT_IDN (('Doe', 'John', '', '', 'PAP.Person'), 'FR83404833048') would clash with 1 existing entities
      Already existing:
        PAP.Company_has_VAT_IDN (('John Doe, Inc.', 'Paris', 'PAP.Company'), 'FR83404833048')

    >>> print (p1.ui_display, ": VAT-IDN =", p1.vat_idn)
    Doe Jane, Dr. : VAT-IDN = GB999999973

    >>> print (c1.ui_display, ": VAT-IDN =", c1.vat_idn)
    Doe Jane, Dr. : VAT-IDN = GB999999973

    >>> print (c2.ui_display, ": VAT-IDN =", c2.vat_idn)
    John Doe, Inc., Paris : VAT-IDN = FR83404833048

    >>> with expect_except (MOM.Error.Invariants) :
    ...     _ = PAP.Company_has_VAT_IDN (c3, vin = "GB999 9999 73") # doctest:+ELLIPSIS
    Invariants: The attribute values for 'vin' must be unique for each object
      The new definition of Company_has_VAT_IDN PAP.Company_has_VAT_IDN (('Jane Doe, Inc.', 'Paris', 'PAP.Company'), 'GB999999973') would clash with 1 existing entities
      Already existing:
        PAP.Person_has_VAT_IDN (('Doe', 'Jane', '', 'Dr.', 'PAP.Person'), 'GB999999973')


    Tests for Attr.Queriers

    >>> print (formatted (PAP.Subject_has_VAT_IDN.E_Type.left.eligible_e_types))
    { 'PAP.Company'
    , 'PAP.Person'
    }
    >>> print (formatted (PAP.Subject_has_VAT_IDN.E_Type.left.selectable_e_types))
    { 'PAP.Company'
    , 'PAP.Person'
    }
    >>> print (formatted (PAP.Subject_has_VAT_IDN.E_Type.left.allow_e_types_transitive))
    set()
    >>> print (formatted (PAP.Subject_has_VAT_IDN.E_Type.left.only_e_types))
    set()
    >>> print (formatted (PAP.Subject_has_VAT_IDN.E_Type.left.refuse_e_types))
    { 'PAP.Adhoc_Group'
    , 'PAP.Company_1P'
    }
    >>> print (formatted (PAP.Subject_has_VAT_IDN.E_Type.left.refuse_e_types_transitive))
    {'PAP.Company_1P'}

    >>> print (formatted (PAP.Company_has_VAT_IDN.E_Type.left.selectable_e_types))
    {'PAP.Company'}
    >>> print (formatted (PAP.Company_has_VAT_IDN.AQ.left.E_Types_AQ))
    {}
    >>> print (formatted (PAP.Company_has_VAT_IDN.AQ.left.E_Types_CNP))
    {}

    >>> print (formatted (PAP.Company_has_VAT_IDN.AQ.As_Json_Cargo ["filters"]))
    [ { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'name'
            , 'sig_key' : 3
            , 'ui_name' : 'Name'
            }
          , { 'name' : 'registered_in'
            , 'sig_key' : 3
            , 'ui_name' : 'Registered in'
            }
          , { 'attrs' :
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
            , 'name' : 'lifetime'
            , 'ui_name' : 'Lifetime'
            }
          , { 'name' : 'short_name'
            , 'sig_key' : 3
            , 'ui_name' : 'Short name'
            }
          , { 'name' : 'vat_idn'
            , 'sig_key' : 0
            , 'ui_name' : 'Vat idn'
            }
          ]
      , 'name' : 'left'
      , 'sig_key' : 2
      , 'ui_name' : 'Company'
      }
    , { 'name' : 'vin'
      , 'sig_key' : 0
      , 'ui_name' : 'VAT id-no'
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

    >>> print (formatted (PAP.Subject_has_VAT_IDN.AQ.As_Json_Cargo ["filters"]))
    [ { 'Class' : 'Entity'
      , 'children_np' :
          [ { 'Class' : 'Entity'
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
          ]
      , 'default_child' : 'PAP.Person'
      , 'name' : 'left'
      , 'sig_key' : 2
      , 'ui_name' : 'Subject'
      }
    , { 'name' : 'vin'
      , 'sig_key' : 0
      , 'ui_name' : 'VAT id-no'
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

_test_qr = r"""
    >>> nav_root = create_app () # doctest:+ELLIPSIS
    Cache ...

    >>> scope = nav_root.scope
    >>> cad   = nav_root.ET_Map ["PAP.Company_has_VAT_IDN"].admin
    >>> ETT   = cad.Templateer.get_template ("e_type")
    >>> QR    = cad.QR
    >>> afl   = QR.Filter (cad.E_Type, "left")

    >>> print ((formatted (afl)))
    Record
      ( AQ = <left.AQ [Attr.Type.Querier Id_Entity]>
      , Class = 'Entity'
      , attr = Company `left`
      , attrs =
        [ Record
            ( attr = String `name`
            , full_name = 'left.name'
            , id = 'left__name'
            , name = 'name'
            , sig_key = 3
            , ui_name = 'Company/Name'
            )
        , Record
            ( attr = String `registered_in`
            , full_name = 'left.registered_in'
            , id = 'left__registered_in'
            , name = 'registered_in'
            , sig_key = 3
            , ui_name = 'Company/Registered in'
            )
        , Record
            ( attr = Date_Interval `lifetime`
            , attrs =
              [ Record
                  ( attr = Date `start`
                  , attrs =
                    [ Record
                        ( attr = Int `day`
                        , full_name = 'left.lifetime.start.day'
                        , id = 'left__lifetime__start__day'
                        , name = 'day'
                        , sig_key = 0
                        , ui_name = 'Company/Lifetime/Start/Day'
                        )
                    , Record
                        ( attr = Int `month`
                        , full_name = 'left.lifetime.start.month'
                        , id = 'left__lifetime__start__month'
                        , name = 'month'
                        , sig_key = 0
                        , ui_name = 'Company/Lifetime/Start/Month'
                        )
                    , Record
                        ( attr = Int `year`
                        , full_name = 'left.lifetime.start.year'
                        , id = 'left__lifetime__start__year'
                        , name = 'year'
                        , sig_key = 0
                        , ui_name = 'Company/Lifetime/Start/Year'
                        )
                    ]
                  , full_name = 'left.lifetime.start'
                  , id = 'left__lifetime__start'
                  , name = 'start'
                  , sig_key = 0
                  , ui_name = 'Company/Lifetime/Start'
                  )
              , Record
                  ( attr = Date `finish`
                  , attrs =
                    [ Record
                        ( attr = Int `day`
                        , full_name = 'left.lifetime.finish.day'
                        , id = 'left__lifetime__finish__day'
                        , name = 'day'
                        , sig_key = 0
                        , ui_name = 'Company/Lifetime/Finish/Day'
                        )
                    , Record
                        ( attr = Int `month`
                        , full_name = 'left.lifetime.finish.month'
                        , id = 'left__lifetime__finish__month'
                        , name = 'month'
                        , sig_key = 0
                        , ui_name = 'Company/Lifetime/Finish/Month'
                        )
                    , Record
                        ( attr = Int `year`
                        , full_name = 'left.lifetime.finish.year'
                        , id = 'left__lifetime__finish__year'
                        , name = 'year'
                        , sig_key = 0
                        , ui_name = 'Company/Lifetime/Finish/Year'
                        )
                    ]
                  , full_name = 'left.lifetime.finish'
                  , id = 'left__lifetime__finish'
                  , name = 'finish'
                  , sig_key = 0
                  , ui_name = 'Company/Lifetime/Finish'
                  )
              , Record
                  ( attr = Boolean `alive`
                  , choices =
                    [ 'no'
                    , 'yes'
                    ]
                  , full_name = 'left.lifetime.alive'
                  , id = 'left__lifetime__alive'
                  , name = 'alive'
                  , sig_key = 1
                  , ui_name = 'Company/Lifetime/Alive'
                  )
              ]
            , full_name = 'left.lifetime'
            , id = 'left__lifetime'
            , name = 'lifetime'
            , ui_name = 'Company/Lifetime'
            )
        , Record
            ( attr = String `short_name`
            , full_name = 'left.short_name'
            , id = 'left__short_name'
            , name = 'short_name'
            , sig_key = 3
            , ui_name = 'Company/Short name'
            )
        , Record
            ( attr = VAT-IDN `vat_idn`
            , full_name = 'left.vat_idn'
            , id = 'left__vat_idn'
            , name = 'vat_idn'
            , sig_key = 0
            , ui_name = 'Company/Vat idn'
            )
        ]
      , edit = None
      , full_name = 'left'
      , id = 'left___AC'
      , name = 'left___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 2
      , type_name = 'PAP.Company'
      , ui_name = 'Company'
      , ui_type_name = 'Company'
      , value = None
      )

"""

_test_saw = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_table (apt, apt._SAW.et_map ["PAP.Subject_has_VAT_IDN"])
    PAP.Subject_has_VAT_IDN (MOM.Id_Entity) <Table pap_subject_has_vat_idn>
        Column left                      : Integer              Link_Role__Init_Only Subject left Id_Entity()
        Column pid                       : Integer              Internal__Just_Once Surrogate pid primary ForeignKey('mom_id_entity.pid')
        Column vin                       : Text                 Primary VAT-IDN vin

    >>> show_table (apt, apt._SAW.et_map ["PAP.Company_has_VAT_IDN"])
    PAP.Company_has_VAT_IDN (PAP.Subject_has_VAT_IDN) PAP.Subject_has_VAT_IDN <Table pap_company_has_vat_idn>
        Column pid                       : Integer              Internal__Just_Once Surrogate pid primary ForeignKey('pap_subject_has_vat_idn.pid')

    >>> show_table (apt, apt._SAW.et_map ["PAP.Person_has_VAT_IDN"])
    PAP.Person_has_VAT_IDN (PAP.Subject_has_VAT_IDN) PAP.Subject_has_VAT_IDN <Table pap_person_has_vat_idn>
        Column pid                       : Integer              Internal__Just_Once Surrogate pid primary ForeignKey('pap_subject_has_vat_idn.pid')

    >>> for tn in ("PAP.Subject_has_VAT_IDN", "PAP.Company_has_VAT_IDN", "PAP.Person_has_VAT_IDN") :
    ...     T   = apt [tn]
    ...     ETW = T._SAW
    ...     ui  = ETW.unique_i
    ...     uo  = ETW.unique_o
    ...     if T.show_in_ui and ETW.unique :
    ...         tail = "" if ui == uo else \\
    ...             (((" + " if ui else "") + ", ".join (uo)) if uo else " =")
    ...         print (("%%-30s %%s%%s" %% (ETW.type_name, ", ".join (ui), tail)).strip ())
    PAP.Subject_has_VAT_IDN        left, vin
    PAP.Company_has_VAT_IDN        left, vin =
    PAP.Person_has_VAT_IDN         left, vin =

    >>> qr_ShV = apt.DBW.PNS.Q_Result.E_Type (apt ["PAP.Subject_has_VAT_IDN"], _strict = False)
    >>> qr_ChV = apt.DBW.PNS.Q_Result.E_Type (apt ["PAP.Company_has_VAT_IDN"], _strict = False)
    >>> qr_PhV = apt.DBW.PNS.Q_Result.E_Type (apt ["PAP.Person_has_VAT_IDN"], _strict = False)

    >>> print (qr_ShV.filter (left = 1))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_subject_has_vat_idn."left" AS pap_subject_has_vat_idn_left,
           pap_subject_has_vat_idn.pid AS pap_subject_has_vat_idn_pid,
           pap_subject_has_vat_idn.vin AS pap_subject_has_vat_idn_vin
         FROM mom_id_entity
           JOIN pap_subject_has_vat_idn ON mom_id_entity.pid = pap_subject_has_vat_idn.pid
         WHERE pap_subject_has_vat_idn."left" = :left_1

    >>> print (qr_ChV.filter (left = 1))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_company_has_vat_idn.pid AS pap_company_has_vat_idn_pid,
           pap_subject_has_vat_idn."left" AS pap_subject_has_vat_idn_left,
           pap_subject_has_vat_idn.pid AS pap_subject_has_vat_idn_pid,
           pap_subject_has_vat_idn.vin AS pap_subject_has_vat_idn_vin
         FROM mom_id_entity
           JOIN pap_subject_has_vat_idn ON mom_id_entity.pid = pap_subject_has_vat_idn.pid
           JOIN pap_company_has_vat_idn ON pap_subject_has_vat_idn.pid = pap_company_has_vat_idn.pid
         WHERE pap_subject_has_vat_idn."left" = :left_1

    >>> print (qr_PhV.filter (left = 1))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_person_has_vat_idn.pid AS pap_person_has_vat_idn_pid,
           pap_subject_has_vat_idn."left" AS pap_subject_has_vat_idn_left,
           pap_subject_has_vat_idn.pid AS pap_subject_has_vat_idn_pid,
           pap_subject_has_vat_idn.vin AS pap_subject_has_vat_idn_vin
         FROM mom_id_entity
           JOIN pap_subject_has_vat_idn ON mom_id_entity.pid = pap_subject_has_vat_idn.pid
           JOIN pap_person_has_vat_idn ON pap_subject_has_vat_idn.pid = pap_person_has_vat_idn.pid
         WHERE pap_subject_has_vat_idn."left" = :left_1

    >>> show_query (qr_PhV.filter (Q.vin.STARTSWITH ("AT"), left = 1))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_person_has_vat_idn.pid AS pap_person_has_vat_idn_pid,
           pap_subject_has_vat_idn."left" AS pap_subject_has_vat_idn_left,
           pap_subject_has_vat_idn.pid AS pap_subject_has_vat_idn_pid,
           pap_subject_has_vat_idn.vin AS pap_subject_has_vat_idn_vin
         FROM mom_id_entity
           JOIN pap_subject_has_vat_idn ON mom_id_entity.pid = pap_subject_has_vat_idn.pid
           JOIN pap_person_has_vat_idn ON pap_subject_has_vat_idn.pid = pap_person_has_vat_idn.pid
         WHERE (pap_subject_has_vat_idn.vin LIKE :vin_1 || '%%%%')
            AND pap_subject_has_vat_idn."left" = :left_1
    Parameters:
         left_1               : 1
         vin_1                : 'AT'

"""

from   _GTW.__test__.model               import *
from   _GTW.__test__._SAW_test_functions import show_query, show_table
from   _MOM.import_MOM                   import Q
from   _TFL.pyk                          import pyk

import _GTW._OMP._PAP.Company_1P
import _GTW._OMP._PAP.Subject_has_VAT_IDN
import _GTW._OMP._PAP.Company_has_VAT_IDN
import _GTW._OMP._PAP.Person_has_VAT_IDN

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_main        = _test_code
        , test_qr          = _test_qr
        )
    )

__test__.update \
    ( Scaffold.create_test_dict \
        ( dict
            ( test_saw     = _test_saw
            )
        , ignore           = ("HPS", "MYS")
        )
    )

### __END__ GTW.__test__.Subject_has_VAT_IDN
