# -*- coding: utf-8 -*-
# Copyright (C) 2004-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CAL._DTW_
#
# Purpose
#    Root for `datetime` wrappers
#
# Revision Dates
#    14-Oct-2004 (CT) Creation
#    17-Oct-2004 (CT) Use `self.Delta` instead of import
#    17-Oct-2004 (CT) `_delta` changed to not look at `_body`
#    23-Oct-2004 (CT) `formatted` changed to use `_default_format`
#    23-Oct-2004 (CT) `_new_object` factored
#    12-Dec-2004 (CT) `__repr__` added
#     9-Aug-2006 (CT) `__hash__` changed to return `hash (self._body)`
#                     instead of `id (self)`
#    30-Nov-2006 (CT) Empty `__getattr__` added to allow cooperative super
#                     calls for `__getattr__` to fail gracefully
#    12-Dec-2006 (CT) `__init__` changed to use `0` as defaults unless
#                     a True `default_to_now` is passed in
#    12-Dec-2006 (CT) `_new_object` changed from `** kw` to `kw`
#     4-Jan-2007 (CT) `__init__` changed to use `1` for date-fields and `0`
#                     for time-fields as defaults
#     4-Jan-2007 (CT) `__init__` changed to use `localtime` if no args or kw
#                     are passed in (and `default_to_now` removed)
#    31-Mar-2008 (CT) `__init__` changed to dereference `_body` if necessary
#     3-May-2011 (CT) `_init_kw` added and used for `__repr__`
#    29-Mar-2012 (CT) Add `_xtra_arg_names` and `_xtra_kw` (to support `tzinfo`)
#     6-May-2015 (CT) Add `_import_cb_json_dump`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#     2-Feb-2016 (CT) Add `new_dtw`, `_Type_Table`, `_DTW_Meta_`
#    12-Feb-2016 (CT) Change `new_dtw` to use `T._kind`, not `cls._kind`
#    17-Jun-2016 (CT) Change `_delta` to wrap `.Delta._Type` instances
#    21-Jun-2016 (CT) Allow single argument of `self._Type` in `__init__`
#    19-Dec-2016 (CT) Add `DT`
#    ««revision-date»»···
#--

from   _CAL                       import CAL
from   _TFL                       import TFL

from   _TFL.pyk                   import pyk
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object
import _TFL._Meta.Property
import _TFL.Accessor

import datetime
import time

class _DTW_Meta_ (TFL.Meta.Object.__class__) :
    """Meta class for _DTW_"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        TT = cls._Type_Table
        for T in (cls._Type, getattr (cls, "Class", None)) :
            if T is not None :
                TT [T] = cls
    # end def __init__

# end class _DTW_Meta_

@totally_ordered
class _DTW_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _DTW_Meta_)) :
    """Root for `datetime` wrappers"""

    _Type            = None
    _Type_Table      = {}
    _default_format  = None
    _kind            = None
    _init_arg_names  = ()
    _init_arg_map    = {}
    _timetuple_slice = None
    _xtra_arg_names  = ()

    _body            = property \
        ( lambda self        : getattr (self, self._kind)
        , lambda self, value : setattr (self, self._kind, value)
        )

    strftime         = property (TFL.Getter._body.strftime)

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (** kw)
        k = self._kind
        if k in kw :
            assert len (args) == 0
            assert len (kw)   == 1
            body = kw [k]
            self._init_kw = {}
            if isinstance (body, _DTW_) :
                body = body._body
                self._init_kw = body._init_kw
            self._body = body
        elif len (args) == 1 and isinstance (args [0], self._Type) :
            assert len (kw)   == 0
            self._init_kw = {}
            self._body    = args [0]
        else :
            if len (args) + len (kw) == 0 :
                defaults = time.localtime ()
            else :
                defaults = (1, 1, 1, 0, 0, 0, 0, 0, 0)
            args += self._timetuple_slice (defaults) [len (args):]
            attrs = self._init_kw = {}
            xkw   = self._xtra_kw = dict (kw)
            for i, name in enumerate (self._init_arg_names) :
                attrs [name] = xkw.pop (name, args [i])
            for name in self._xtra_arg_names :
                if name in xkw :
                    attrs [name] = xkw.pop (name)
            self._body = self._new_object (attrs)
    # end def __init__

    @property
    def DT (self) :
        """Wrapped datetime specific instance."""
        return self._body
    # end def DT

    @TFL.Meta.Class_and_Instance_Method
    def new_dtw (soc, body) :
        T = soc._Type_Table.get (body.__class__)
        if T is not None :
            return T (** {T._kind : body})
        raise TypeError ("Can't create a new wrapper from %s: %s" % (soc, body))
    # end def new_dtw

    def formatted (self, format = None) :
        if format is None :
            format = self._default_format
        return self.strftime (format)
    # end def formatted

    def replace (self, ** kw) :
        return self.__class__ (** {self._kind : self._body.replace (** kw)})
    # end def replace

    def _delta (self, delta) :
        result = delta
        if isinstance (delta, pyk.int_types + (float, )) :
            result = self.Delta (delta)
        elif isinstance (delta, self.Delta._Type) :
            result = _DTW_.new_dtw (delta)
        return result
    # end def _delta

    def _init_arg (self, name) :
        if self._init_kw :
            return self._init_kw.get (name)
        else :
            return getattr (self, self._init_arg_map.get (name, name), 0)
    # end def _init_arg

    def _new_object (self, kw) :
        return self._Type (** kw)
    # end def _new_object

    def __eq__ (self, rhs) :
        return self._body == getattr (rhs, self._kind, rhs)
    # end def __eq__

    def __getattr__ (self, name) :
        raise AttributeError (name)
    # end def __getattr__

    def __hash__ (self) :
        return hash (self._body)
    # end def __hash__

    def __lt__ (self, rhs) :
        return self._body < getattr (rhs, self._kind, rhs)
    # end def __lt__

    def __str__ (self) :
        return str (self._body)
    # end def __str__

    def __repr__ (self) :
        return "%s (%s)" % \
            ( self.__class__.__name__
            , ", ".join
                (repr (self._init_arg (a)) for a in self._init_arg_names)
            )
    # end def __repr__

# end class _DTW_

@totally_ordered
class _Mutable_DTW_ (TFL.Meta.Object) :
    """Root for mutable `datetime` wrappers"""

    def __init__ (self, * args, ** kw) :
        self._wrapped = self.Class (* args, ** kw)
    # end def __init__

    def replace (self, ** kw) :
        self._wrapped = self._wrapped.replace (** kw)
        return self
    # end def replace

    def __add__ (self, rhs) :
        return self.__class__ (** {self.Class._kind : self._wrapped + rhs})
    # end def __add__

    def __eq__ (self, rhs) :
        return self._wrapped == rhs
    # end def __eq__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self._wrapped, name)
    # end def __getattr__

    def __hash__ (self) :
        raise KeyError ("%s is not hashable")
    # end def __hash__

    def __iadd__ (self, rhs) :
        self._wrapped += rhs
        return self
    # end def __iadd__

    def __isub__ (self, rhs) :
        self._wrapped -= rhs
        return self
    # end def __isub__

    def __lt__ (self, rhs) :
        return self._wrapped < rhs
    # end def __lt__

    def __sub__ (self, rhs) :
        return self.__class__ (** {self.Class._kind : self._wrapped - rhs})
    # end def __sub__

    __str__ = property (lambda s : s._wrapped.__str__)

# end class _Mutable_DTW_

@TFL._Add_Import_Callback ("_TFL.json_dump")
def _import_cb_json_dump (module) :
    @module.default.add_type (_DTW_, _Mutable_DTW_)
    def json_encode_cal (o) :
        try :
            encoder = o._body.isoformat
        except AttributeError :
            encoder = o.__str__
        return encoder ()
# end def _import_cb_json_dump

if __name__ != "__main__" :
    CAL._Export ("_DTW_", "_Mutable_DTW_")
### __END__ CAL._DTW_
