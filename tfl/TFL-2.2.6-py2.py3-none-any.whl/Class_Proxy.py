#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2001-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Class_Proxy
#
# Purpose
#    Transparent proxy for a class
#
# Revision Dates
#     5-Feb-2001 (CT) Creation
#    19-Jul-2001 (CT) Redefinition of `__call__` replaced by aliasing
#                     `__call__` to `Class`
#    17-Aug-2001 (CT) Define `__call__` as method instead of assigning it
#                     to `_Class` inside `__init__` (otherwise, descendent
#                     classes have a hard time redefining `__call__`)
#    10-Jan-2005 (CT) `__repr__` changed to not future warn about negative
#                     values of `id`
#    ««revision-date»»···
#--

from   __future__               import print_function

class Class_Proxy :
    """Transparent proxy for a class."""

    def __init__ (self, Class) :
        self.__dict__ ["_Class"]   = Class
    # end def __init__

    def __getattr__ (self, name) :
        if not (name.startswith ("__") and name.endswith ("__")) :
            return self._delegate_attribute (name)
        raise AttributeError (name)
    # end def __getattr__

    def __call__ (self, * args, ** kw) :
        self._Class (* args, ** kw)
    # end def __call__

    def __hash__ (self) :
        return hash (self._Class)
    # end def __hash__

    def __str__ (self) :
        return str (self._Class)
    # end def __str__

    def __repr__ (self) :
        return "<%s for %s>" % (self.__class__.__name__, repr (self._Class))
    # end def __repr__

    def __setattr__ (self, name, value) :
        setattr (self._Class, name, value)
    # end def __setattr__

    def _delegate_attribute (self, name) :
        """Redefine in descendents as necessary"""
        return getattr (self._Class, name)
    # end def _delegate_attribute

# end class Class_Proxy

def isinstance_cp (object, C, isinstance = isinstance) :
    ### print ("isinstance", object, C)
    ### from caller_globals import caller_info
    ### print ("isinstance", caller_info ())
    if hasattr (C, "_Class") :
        C = C._Class
    return isinstance (object, C)
# end def isinstance_cp

def issubclass_cp (C, B, issubclass = issubclass) :
    ### print ("issubclass", C, B)
    ### from caller_globals import caller_info
    ### print ("isinstance", caller_info ())
    if hasattr (C, "_Class") : C = C._Class
    if hasattr (B, "_Class") : B = B._Class
    return issubclass (C, B)
# end def issubclass_cp

from _TFL import TFL
TFL._Export ("*")

### __END__ Class_Proxy
