# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer. All rights reserved
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
#    MOM.Pred.__init__
#
# Purpose
#    Initialize package `MOM.Pred`
#
# Revision Dates
#    17-Sep-2009 (CT) Creation (factored from TOM.Pred)
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Package_Namespace
from   _MOM                   import MOM

Pred = Package_Namespace ()
MOM._Export ("Pred")

del Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`MOM.Pred` provides a framework for the definition and
implementation of essential and non-essential predicates of
:class:`objects<_MOM.Object.Object>`
and :class:`links<_MOM.Link.Link>` of essential object models.

A predicate defines a condition that must be satisfied by the
instances of an essential class or association. Some predicates must
hold at all times during the life of an entity (commonly called
`invariants`_), others must only be satisfied at certain points in
time.

Predicates ensure the consistency and correctness of an essential
object model, they protect an application against incorrect and/or
incomplete input data, and they protect the user against non-sensical
output from the application.

Whenever possible, predicates should be used to define the input and
output constraints on the application. This simplifies the algorithms
used to implement the application because each algorithm can (and
should) assume correct input data and thus doesn't need to check for
and handle errors.

Each predicate is characterized by

- its :class:`type<_MOM._Pred.Type._Condition_>`

- its :class:`kind<_MOM._Pred.Kind.Kind>`

The predicates are defined inside the class definition of the
essential entity, i.e., object or link, and are encapsulated inside a
class named `_Predicates` that is derived from
:class:`~_MOM._Pred.Spec.Spec`, for instance::

    from _MOM._Pred import Pred

    class Some_Essence (MOM.Object) :

        class _Predicates (MOM.Object._Predicates) :

            class completely_defined (Pred.Condition) :
                "All necessary attributes must be defined."

                kind          = Pred.System
                guard         = "is_used"
                guard_attr    = ("is_used", )

                ...

The predicates of a specific instance of an essential entity are
managed by an instance of :class:`~_MOM._Pred.Manager.Manager`.

.. _`invariants`: http://en.wikipedia.org/wiki/Class_invariant

How to write a predicate
------------------------

* Keep it simple

  - correctness should be obvious

  - use `bindings` to simplify `assertion`

* Think about the user

  - provide a meaningful description

  - provide information about the violating values (include expressions in
    `parameters` and/or `bvar_attr` if necessary)

  - provide information about the violating elements of the set that is
    quantified over

  - don't hesitate to add cached or computed attributes to make
    more information visible to the user

* Think about the maintenance programmer

  - avoid redundancy

  - make it readable

* Keep it declarative

  - don't call functions unless absolutely necessary

  - don't hesitate to add cached or computed attributes to simplify
    the assertion

  - use `assertion` to define the logical condition of the predicate

  - don't ever redefine `eval_condition`

* Keep performance in mind

  - care about Big-O behavior

  - think about where to put it (each assertion should be evaluated
    only once for a given (set of) objects)

  - avoid traversing significant parts of the object model during
    evaluation of a single predicate

  - don't hesitate to add cached or computed attributes to improve
    performance


"""

### __END__ MOM.Pred.__init__
