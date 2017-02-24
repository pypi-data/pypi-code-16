# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Company_1P
#
# Purpose
#    Test PAP.Company_1P
#
# Revision Dates
#     5-Feb-2016 (CT) Creation
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
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

    >>> PAP.Company_1P.polish_attr
    (String `name`,)

    >>> p1 = PAP.Person ("Doe", "Jane", title = "Dr.", raw = True)
    >>> print (p1.ui_repr)
    PAP.Person ('Doe', 'Jane', '', 'Dr.')
    >>> print (p1.ui_display)
    Doe Jane, Dr.

    >>> c1 = PAP.Company_1P (person = p1, raw = True)
    >>> print (c1.ui_repr)
    PAP.Company_1P (('Doe', 'Jane', '', 'Dr.', 'PAP.Person'), 'Doe Jane, Dr.', '')

"""

_test_saw = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_table (apt, apt._SAW.et_map ["PAP.Company"])
    PAP.Company (MOM.Id_Entity) <Table pap_company>
        Column __raw_name                : Varchar(64)          Primary__Raw_Value String name
        Column __raw_registered_in       : Varchar(64)          Primary_Optional__Raw_Value String registered_in
        Column __raw_short_name          : Varchar(12)          Optional__Raw_Value String short_name
        Column lifetime__finish          : Date                 Optional__Nested__Structured Date finish
        Column lifetime__start           : Date                 Necessary__Nested__Structured Date start
        Column name                      : Varchar(64)          Primary__Raw_Value String name
        Column pid                       : Integer              Internal__Just_Once Surrogate pid primary ForeignKey('mom_id_entity.pid')
        Column registered_in             : Varchar(64)          Primary_Optional__Raw_Value String registered_in
        Column short_name                : Varchar(12)          Optional__Raw_Value String short_name

    >>> show_table (apt, apt._SAW.et_map ["PAP.Company_1P"])
    PAP.Company_1P (PAP.Company) PAP.Company <Table pap_company_1p>
        Column person                    : Integer              Primary__Id_Entity_Reference Entity person Id_Entity()
        Column pid                       : Integer              Internal__Just_Once Surrogate pid primary ForeignKey('pap_company.pid')

"""

from   _GTW.__test__.model               import *
from   _GTW.__test__._SAW_test_functions import show_table
from   _MOM.import_MOM                   import Q
from   _MOM.Inspect                      import children_trans_iter
from   _TFL.pyk                          import pyk

import _GTW._OMP._PAP.Company_1P

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_main        = _test_code
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

### __END__ GTW.__test__.Company_1P
