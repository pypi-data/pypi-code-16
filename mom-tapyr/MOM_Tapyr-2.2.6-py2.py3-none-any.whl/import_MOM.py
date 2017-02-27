# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.import_MOM
#
# Purpose
#    Provide all imports necessary to define application-specific essential
#    classes based on the MOM meta object model
#
#    Usage:
#        from MOM.import_MOM import *
#
# Revision Dates
#    22-Oct-2009 (CT) Creation
#     7-Dec-2009 (CT) `Q` added
#    22-Dec-2009 (CT) `Sequence_Number` removed
#     4-May-2010 (CT) `Q` moved to `MOM.Attr.Type`
#     5-Jul-2011 (CT) `MOM.Attr.Selector` added
#    19-Jul-2011 (CT) `MOM.Q_Exp_Raw` added
#    15-Jun-2013 (CT) Import `Derived_PNS`
#     9-Sep-2014 (CT) Rename `MOM.Q_Exp_Raw` to `MOM.Q_Exp`
#    14-Sep-2015 (CT) Add `import_full_model`
#    13-Oct-2015 (CT) Add `import` for `_TFL.fix_datetime_pickle_2_vs_3`
#    29-May-2016 (CT) Add `MOM.Selector`
#    19-Jul-2016 (CT) Add `MOM.Attr.Date_Time`, `MOM.Attr.Structured`
#    ««revision-date»»···
#--

from   _MOM import MOM
from   _TFL import TFL

import _MOM.App_Type
import _MOM.Entity
import _MOM.Error
import _MOM.Link
import _MOM.Object
import _MOM.Q_Exp
import _MOM.Selector
import _MOM.Scope

import _MOM._Attr.Selector

from   _MOM._Attr.Type       import *
from   _MOM._Attr            import Attr
from   _MOM._Pred            import Pred
from   _MOM._Attr.Date_Time  import *
from   _MOM._Attr.Structured import *

import _MOM.Derived_PNS

import _TFL.fix_datetime_pickle_2_vs_3

def import_full_model () :
    """Import all essential classes defined by MOM."""
    import _MOM.Document
    import _MOM.Id_Entity_has_Tag
# end def import_full_model

MOM._Export ("import_full_model")

### __END__ MOM.import_MOM
