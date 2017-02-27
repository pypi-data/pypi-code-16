# -*- coding: utf-8 -*-
# Copyright (C) 2003-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    module_copy
#
# Purpose
#    Return an independent copy of a module
#
# Revision Dates
#    17-Dec-2003 (CT) Creation
#    ««revision-date»»···
#--

import sys

def module_copy (name, ** kw) :
    """Return an independent copy of the module with `name` and assign all
       elements of `kw` to the result.
    """
    original = None
    if name in sys.modules :
        original = sys.modules [name]
        del sys.modules [name]
        try :
            result = __import__ (name, {}, {})
        finally :
            sys.modules [name] = original
    else :
        result = __import__ (name, {}, {})
        del sys.modules [name]
    for k, v in kw.items () :
        setattr (result, k, v)
    return result
# end def module_copy

def import_module_copy (name, as_name, ** kw) :
    """Put a module_copy with `name` into `sys.modules`."""
    result = sys.modules [as_name] = module_copy (name, ** kw)
    return result
# end def import_module_copy

if __name__ != "__main__" :
    from _TFL import TFL
    TFL._Export ("*")
### __END__ module_copy
