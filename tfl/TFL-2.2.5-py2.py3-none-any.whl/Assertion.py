# -*- coding: utf-8 -*-
# Copyright (C) 2002-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Assertion
#
# Purpose
#    Provide Assert function nicer than Python's assert statement
#
# Revision Dates
#     8-Jul-2002 (CT) Creation (factored from U_Test.py)
#    24-Mar-2005 (CT) Use `TFL.Caller.globals` instead of `caller_globals`
#                     (and ditto for `locals`)
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL.Caller

def _test_assertion (expr, locals, msg = "", expression = None) :
    if not expr :
        tail  = []
        items = locals.items ()
        items.sort ()
        for k, v in items :
            if k == "self" or k [0] == "_" : continue
            tail.append ("%-20s = %r" % (k, v))
        msg = \
            ( "%s\n    %s"
            % ( ", ".join     (x for x in (expression, msg) if x)
              , "\n    ".join (tail)
              )
            )
        raise AssertionError (msg)
# end def _test_assertion

def Assertion (expression, msg = "") :
    """Perform the equivalent of `assert` on `eval (expression)`.

       There are two differences to standard `assert`:

       - all elements of `locals` and of the caller's local name space
         are shown in the message passed to `AssertionError`

       - A false value of `__debug__` doesn't prevent the check of
         `expression`
    """
    locals = TFL.Caller.locals ()
    try :
        result = eval (expression, TFL.Caller.globals (), locals)
    except Exception as exc :
        _test_assertion (0,      locals, str (exc), expression)
    _test_assertion     (result, locals, msg,       expression)
# end def Assertion

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Assertion
