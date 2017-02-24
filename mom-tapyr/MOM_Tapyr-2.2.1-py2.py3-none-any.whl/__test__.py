# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.__test__
#
# Purpose
#    Some helper functions for MOM related testing
#
# Revision Dates
#    18-Feb-2010 (MG) Creation
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#    ««revision-date»»···
#--

from   _MOM.import_MOM           import *
from   _MOM.Product_Version      import Product_Version, IV_Number

Version = Product_Version \
    ( productid           = u"GTW Test"
    , productnick         = u"GTW"
    , productdesc         = u"Example web application "
    , date                = "20-Jan-2010"
    , major               = 0
    , minor               = 5
    , patchlevel          = 42
    , author              = u"Christian Tanzer, Martin Glück"
    , copyright_start     = 2010
    , db_version          = IV_Number
        ( "db_version"
        , ("Hello World", )
        , ("Hello World", )
        , program_version = 1
        , comp_min        = 0
        , db_extension    = ".how"
        )
    )

def define_app_type (name, PKG, EMS, DBW) :
    if name not in MOM.App_Type.Table :
        PKG.Version = Version
        MOM.App_Type (name, PKG)
    app = MOM.App_Type.Table [name]
    return app.Derived (EMS, DBW)
# end def define_app_type

### __END__ __test__
