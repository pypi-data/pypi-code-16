# -*- coding: utf-8 -*-
# Copyright (C) 2009-2017 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This file is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.__init__
#
# Purpose
#    Package implementing a simple meta object model in python
#
# Revision Dates
#    17-Sep-2009 (CT) Creation (factored from TOM)
#    11-Oct-2016 (CT) Add ``__version__``
#    22-Feb-2017 (CT) Remove `__version__`
#    ««revision-date»»···
#--

from _TFL.Package_Namespace import Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`MOM` provides a framework for the definition and
implementation of essential object models.

An essential (see [McP84]_) object model is one way of
capturing the results of an object oriented analysis. An essential
object model comprises classes and associations.

Each essential class (modelled by a descendent of the class
:class:`MOM.Object<_MOM.Object.Object>`)
describes one specific type of object, in particluar

- the attributes (modelled by the classes in the package namespace
  :mod:`MOM.Attr<_MOM._Attr>`),

- and the predicates (modelled by the classes in the package namespace
  :mod:`MOM.Pred<_MOM._Pred>`)

visible to the class' clients.

Each essential association (modelled by a descendent of the class
:class:`MOM.Link<_MOM.Link.Link>`)
describes the possible links between the objects of a number of classes.

As the links of an association are also characterized by attributes
and predicates, most of the behavior of
:class:`MOM.Object<_MOM.Object.Object>` and
:class:`MOM.Link<_MOM.Link.Link>` is defined by their common ancestor
:class:`MOM.Id_Entity<_MOM.Entity.Id_Entity>`.

A specific meta object model is defined for a well-defined application and
encapsulated by :class:`MOM.App_Type<_MOM.App_Type.App_Type>`. Each
instance of a meta object model is managed by a scope object (modelled by the
class :class:`MOM.Scope<_MOM.Scope.Scope>`).

"""


MOM = Package_Namespace ()

del Package_Namespace

### __END__ MOM.__init__
