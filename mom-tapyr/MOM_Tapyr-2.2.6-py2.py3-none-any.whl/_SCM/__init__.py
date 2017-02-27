# -*- coding: utf-8 -*-
# Copyright (C) 2004-2015 Mag. Christian Tanzer. All rights reserved
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
#    MOM.SCM.__init__
#
# Purpose
#    Initialize package `MOM.SCM`
#
# Revision Dates
#    17-Sep-2009 (CT) Creation (factored from `TOM.Pred`)
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Package_Namespace
from   _MOM                   import MOM

SCM = Package_Namespace ()
MOM._Export ("SCM")

del Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

Requirements
============

Each scope needs to keep track of changes to the its objects:

- Entity changes:

  * create
  * remove
  * rename
  * change:
    . set_cooked
    . set_raw
    . setattr (e.g., foo.bar = 42)

- Model changes:

  * make schedule
  * delete schedule
  * edit schedule
  * run script
  * make MEDL (no change expected)
  * generate code (no change expected)
  * ...

A scope needs a change count (used for deciding when to recompute lazy
functions, e.g., check predicates) and, optionally, a list of change
actions for undo/redo.

Some change actions are composite, i.e., they comprise more than one
change action. For instance,

- removing an objects also removes all its links

- creating an object in an editor might automagigally create links

- running a script might comprise lots of changes

  * beware: it might also switch scopes and do other mischief, i.e.,
    if a script runs a 'File.Load' command, the following changes
    should ideally be encapsulated in a run-script change action of
    the historian of the newly created scope

Normally, a composite action can only be undone as a whole. Undoing a
composite action might just mean undoing all its elementary actions
(in reverse order) or might might mean doing a complementary action
(e.g., deleting a schedule to undo a 'make schedule' action).

Constraints
===========

- Don't keep references to essential objects to avoid memory leaks

  * problem: attributes of types like `A_Id_Entity`

- Store the minimum amount of information in the history list
  necessary to support undo

  * don't store volatile attributes

  * don't store computed attributes

- Make interface to historian as small as possible

- Let `record` instantiate change action objects if necessary (some
  kinds of recorders don't need change action objects so; therefore
  avoid needless instantiations)

- Make historian configurable:

  * keeping a full history costs lots of RAM

  * let user decide on the tradeoff between RAM and redo-comfort

Design
======

Each scope has its own `historian`. A historian manages a change count
and an (optional) list of change actions (history list). For each
change, `historian.record` (or `historian.record_encapsulated`) is
called by the code responsible for the change (scope, entity, or
command manager). `record` uses the current recorder to remember the
change.

There are different kinds of recorders, for instance:

- Ignore: don't do anything (e.g., makes sense during loading of a
  database, during destroying of a scope)

- Counter: just increases the change count

  * might also increase the change count of a dependent scope's
    historian (e.g., NC_use scope has dependent node scope)

- Appender: increases the change count and appends action to the
  history list

  * might append to the historians history list or to the history list
    of a composite action

With changing context, the current recorder of the historian changes.
Each kind of recorder has a specific priority.

`historian.record_encapsulated` records a change action *and* calls a
function (passed as argument) with a temporary recorder which records
into the (composite) change action (passed as argument). The temporary
recorder is chosen by selecting the higher priority recorder of
`historian.recorder` and `change_action.recorder` (i.e., if the
current recorder of the historian is Ignore, the temporary recorder
also will be Ignore, no matter what the preferred recorder of the
change_action would be).

XXX Provide a context manager to be used instead of `record_encapsulated` !!!
"""

### __END__ MOM/SCM/__init__
