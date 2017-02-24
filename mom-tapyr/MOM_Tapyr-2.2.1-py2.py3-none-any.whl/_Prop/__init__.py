# -*- coding: utf-8 -*-
# Copyright (C) 2009-2010 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This package is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Prop.__init__
#
# Purpose
#    Initialize package `MOM.Prop`
#
# Revision Dates
#    24-Sep-2009 (CT) Creation (factored from TOM classes)
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Package_Namespace
from   _MOM                   import MOM

Prop = Package_Namespace ()
MOM._Export ("Prop")

del Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`MOM.Prop` provides a framework for the definition and
implementation of essential attributes and predicates of
:class:`objects<_MOM.Object.Object>`
and :class:`links<_MOM.Link.Link>` of essential object models.


"""

### __END__ MOM.Prop.__init__
