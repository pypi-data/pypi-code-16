# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.PAP.import_PAP
#
# Purpose
#    Import PAP object model
#
# Revision Dates
#    30-Dec-2009 (CT) Creation
#    13-Oct-2010 (CT) `Entity_created_by_Person` added
#    22-Mar-2012 (CT) Add `Company` and its links
#    12-Sep-2012 (CT) Add `Property`, `Subject`, and `Subject_has_Property`,
#                     remove `Company_has_...`, `Person_has_...`
#    11-Oct-2012 (CT) Add `Address_Position`, `Url`
#     6-Dec-2012 (CT) Add `Person_has_Account` (conditional import)
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    16-Apr-2014 (CT) Add `Person_has_Property`
#    15-Sep-2014 (CT) Remove `Person_has_Property`
#    16-Dec-2015 (CT) Use `_Add_Import_Callback` as decorator
#    ««revision-date»»···
#--

from   _MOM.import_MOM        import *
from   _GTW                   import GTW
from   _GTW._OMP._PAP         import PAP

import _GTW._OMP._PAP.Address
import _GTW._OMP._PAP.Company
import _GTW._OMP._PAP.Email
import _GTW._OMP._PAP.Entity
import _GTW._OMP._PAP.Phone
import _GTW._OMP._PAP.Person
import _GTW._OMP._PAP.Property
import _GTW._OMP._PAP.Subject
import _GTW._OMP._PAP.Url

import _GTW._OMP._PAP.Address_Position
import _GTW._OMP._PAP.Subject_has_Property
import _GTW._OMP._PAP.Subject_has_Phone

GTW.OMP.PAP.Subject_has_Property.m_create_role_children ("right")

@GTW._Add_Import_Callback ("_GTW._OMP._Auth.Account")
def _import_person_has_account (module) :
    import _GTW._OMP._PAP.Person_has_Account
# end def _import_person_has_account

### __END__ GTW.OMP.PAP.import_PAP
