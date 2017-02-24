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
#    MOM.Attr.__init__
#
# Purpose
#    Initialize package `MOM.Attr`
#
# Revision Dates
#    17-Sep-2009 (CT) Creation (factored from TOM.Attr)
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Package_Namespace
from   _MOM                   import MOM

Attr = Package_Namespace ()
MOM._Export ("Attr")

del Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`MOM.Attr` provides a framework for the definition and
implementation of essential and non-essential attributes of
:class:`objects<_MOM.Object.Object>`
and :class:`links<_MOM.Link.Link>` of essential object models.

Each attribute is characterized by

- its :class:`type<_MOM._Attr.Type.A_Attr_Type>`

- its :class:`kind<_MOM._Attr.Kind.Kind>`

The attributes are defined inside the class definition of the
essential entity, i.e., object or link, and are encapsulated inside a
class named `_Attributes` that is derived from
:class:`~_MOM._Attr.Spec.Spec`, for instance::

    from _MOM._Attr import Attr

    class Some_Essence (MOM.Object) :

        class _Attributes (MOM.Object._Attributes) :

            class is_used (Attr.A_Int) :
                "Counts the number of users of this object."
                kind          = Attr.Cached
                default       = "1"
            # end class is_used

            ...

The attributes of a specific instance of an essential entity are
managed by an instance of :class:`~_MOM._Attr.Manager.Manager`.

"""

### __END__ MOM.Attr.__init__
