# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Undef
#
# Purpose
#    Provide a class for defining undefined objects with nice repr
#
# Revision Dates
#     3-Sep-2010 (CT) Creation
#    28-Sep-2010 (CT) `__nonzero__` added
#    22-Feb-2013 (CT) Add doc-tests
#    21-Aug-2014 (CT) Add `is_undefined`
#    13-Apr-2015 (CT) Add `_import_cb_json_dump`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL               import TFL
from   _TFL.pyk           import pyk

@pyk.adapt__bool__
class Undef (object) :
    """Undefined object with nice repr."""

    def __init__ (self, name = None) :
        self.name = name
    # end def __init__

    def __bool__ (self) :
        return False
    # end def __bool__

    def __repr__ (self) :
        names = [self.__class__.__name__]
        if self.name :
            names.append (self.name)
        return "<%s>" % "/".join (names)
    # end def __repr__

# end class Undef

def is_undefined (value) :
    """Return True, if `value` is an instance of `Undef`."""
    return isinstance (value, Undef)
# end def is_undefined

@TFL._Add_Import_Callback ("_TFL.json_dump")
def _import_cb_json_dump (module) :
    @module.default.add_type (Undef)
    def json_encode_undef (o) :
        return None
# end def _import_cb_json_dump

__doc__ = """
:class:`Undef` provides a way to define undefined objects with a nice
and deterministic `repr`.

Normally, one would define an undefined object like this::

    >>> undefined = object ()
    >>> bool (undefined)
    True
    >>> undefined # doctest:+ELLIPSIS
    <object object at ...>

This works well, as long as `undefined` doesn't appear in any context, where
it's `repr` is taken and as long as nobody applies boolean tests to it.

:class:`Undef` avoids both these problems::

    >>> undef = Undef ()
    >>> bool (undef)
    False
    >>> undef
    <Undef>

    >>> undefined_foo = Undef ("foo")
    >>> bool (undefined_foo)
    False
    >>> undefined_foo
    <Undef/foo>

    >>> undefined_bar = Undef ("bar")
    >>> bool (undefined_bar)
    False
    >>> undefined_bar
    <Undef/bar>

    >>> undefined_foo == undefined_bar
    False
    >>> undefined_foo is undefined_bar
    False

    >>> undefined_foo == Undef ("foo")
    False
    >>> undefined_foo is Undef ("foo")
    False

.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

if __name__ != "__main__" :
    TFL._Export ("Undef", "is_undefined")
### __END__ TFL.Undef
