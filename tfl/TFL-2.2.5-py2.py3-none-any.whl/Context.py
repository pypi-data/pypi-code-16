# -*- coding: utf-8 -*-
# Copyright (C) 2008-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Context
#
# Purpose
#    Library of context manager functions
#
# Revision Dates
#    14-Apr-2008 (CT) Creation
#    10-Dec-2009 (CT) `attr_let` changed to accept `** kw` instead of a
#                     single name and value
#    17-Dec-2010 (CT) `time_block` added
#    28-Jun-2012 (CT) Add `relaxed`
#    17-Jul-2012 (CT) Augment `AttributeError` info in `attr_let`
#    28-Sep-2012 (CT) Add `try` for `fmt % delta` to `time_block`
#    22-Feb-2013 (CT) Use `TFL.Undef ()` not `object ()`
#    14-Mar-2014 (CT) Add `dict_let`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL                  import TFL
from   _TFL.pyk              import pyk

import _TFL.Decorator
import _TFL.Undef

from   contextlib import closing
from   timeit     import default_timer as _timer

@TFL.Contextmanager
def attr_let (obj, ** kw) :
    """Provide context with attributes of `obj` temporary bound to
       values in `kw`.
    """
    store = {}
    undef = TFL.Undef ()
    for k, v in pyk.iteritems (kw) :
        store [k] = getattr (obj, k, undef)
    try :
        for k, v in pyk.iteritems (kw) :
            try :
                setattr (obj, k, v)
            except AttributeError as exc :
                raise AttributeError ("%s: [%s = %r]" % (exc, k, v))
        yield
    finally :
        for k, v in pyk.iteritems (store) :
            if v is undef :
                delattr (obj, k)
            else :
                try :
                    setattr (obj, k, v)
                except AttributeError as exc :
                    raise AttributeError ("%s: [%s = %r]" % (exc, k, v))
# end def attr_let

@TFL.Contextmanager
def dict_let (dct, ** kw) :
    """Provide context with elements of dictionary `dct` temporary bound to
       values in `kw`.
    """
    store = {}
    undef = TFL.Undef ()
    for k, v in pyk.iteritems (kw) :
        store [k] = dct.get (k, undef)
    try :
        for k, v in pyk.iteritems (kw) :
            dct [k] = v
        yield
    finally :
        for k, v in pyk.iteritems (store) :
            if v is undef :
                del dct [k]
            else :
                dct [k] = v
# end def dict_let

@TFL.Contextmanager
def list_push (list, item) :
    """Context manager for temporarily pushing `item` onto `list`."""
    list.append (item)
    try :
        yield list
    finally :
        assert list [-1] is item
        list.pop ()
# end def list_push

@TFL.Contextmanager
def relaxed (* args, ** kw) :
    """Context manager doing nothing."""
    yield None
# end def relaxed

@TFL.Contextmanager
def time_block (fmt = "Execution time: %s", out = None, cb = None) :
    """Context manager measuring the execution time for a block.

       After finishing the block, `cb` will be called with the arguments
       `start`, `finish`, and `delta`, if specified.

       Otherwise, `time_block` will use `fmt` to write the execution time to
       sys.stdout.
    """
    start  = _timer ()
    yield
    finish = _timer ()
    delta  = finish - start
    if cb is not None :
        cb (start, finish, delta)
    else :
        from _TFL.pyk import pyk
        try :
            msg = fmt % (delta, )
        except (TypeError, ValueError) as exc :
            msg = "%s: %s" % (fmt, delta)
        pyk.fprint (msg, file = out)
# end def time_block

__doc__ = """
Library of context manager functions.

"""

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Context
