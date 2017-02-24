# -*- coding: utf-8 -*-
# Copyright (C) 2005-2014 Martin Glück. All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. office@spannberg.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CAL.iCalendar
#
# Purpose
#    A wrapper around the iCalender library.
#
# Revision Dates
#     7-Dec-2005 (MG) Creation
#     9-Aug-2006 (CT) `__hash__` changed to return
#                     `hash ((self.address, self.role))` instead of `id (self)`
#    29-Aug-2008 (CT) s/super(...)/__m_super/
#    16-Jun-2013 (CT) Use `TFL.CAO`, not `TFL.Command_Line`
#    ««revision-date»»···
#--

from   __future__                 import print_function

from   _CAL                       import CAL
from   _TFL                       import TFL

from   _TFL.pyk                   import pyk
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object
import _TFL._Meta.Property
import _TFL._Meta.M_Class
import _TFL.CAO

import _CAL.Date_Time

import icalendar

class Undefined (object) :

    def __str__ (self) :
        return "UNDEFINED"
    # end def __str__

# end class Undefined

@totally_ordered
class Email (TFL.Meta.Object) :
    """Convert an icalendar vCalAddress property"""

    properties = ("rsvp", "role", "parstat", "cn")

    def __init__ (self, ical) :
        self.address = str (ical).replace ("mailto:", "")
        for p in self.properties :
            setattr (self, p, ical.params.get (p, None))
        self.name = self.address.split ("@") [0].replace (".", " ")
    # end def __init__

    def __repr__ (self) :
        if self.role :
            return "%-15s: %s" % (self.role, self.name)
        return self.name
    # end def __repr__

    __str__ = __repr__

    def __eq__ (self, other) :
        s = self.address,                      self.role
        o = getattr (other, "address", other), getattr (other, "role", other)
        return s == o
    # end def __eq__

    def __hash__ (self) :
        return hash ((self.address, self.role))
    # end def __hash__

    def __lt__ (self, other) :
        s = self.address,                      self.role
        o = getattr (other, "address", other), getattr (other, "role", other)
        return s < o
    # end def __lt__

# end class Email

class ICal_Prop (TFL.Meta.Property) :
    """Proviedes access to the properties of the ical object."""

    conversion = \
        { icalendar.prop.vText       : str
        , icalendar.prop.vDDDTypes   : CAL.Date_Time.from_ical
        , icalendar.prop.vCalAddress : Email
        }

    undefined = Undefined ()

    def get_value (self, obj) :
        value = obj._attributes.get (self.name, self.undefined)
        if value is self.undefined :
            value = self._get_value (obj)
            obj._attributes [self.name] = value
        return value
    # end def get_value
    _get = get_value

    def _get_value (self, obj) :
        try :
            value = obj._icomp [self.name]
        except KeyError as exc:
            raise AttributeError (exc)
        if value.__class__ in self.conversion :
            value = self.conversion [value.__class__] (value)
        return value
    # end def _get_value

# end class ICal_Prop

class ICal_Multi_Prop (ICal_Prop) :
    """A property which should be a list of values."""

    def _get_value (self, obj) :
        try :
            values = obj._icomp [self.name]
        except KeyError as exc:
            raise AttributeError (exc)
        if not isinstance (values, (list, tuple)) :
            values = (values, )
        result = []
        for value in values :
            if value.__class__ in self.conversion :
                value = self.conversion [value.__class__] (value)
            result.append (value)
        return result
    # end def _get_value

# end class ICal_Multi_Prop

class M_ICalendar (TFL.Meta.M_Class) :
    """Meta class for the wrapper for the icalendar classes."""

    prop_conversion = {}

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        wrapped                 = cls.wrapped
        cls.properties          = ()
        if wrapped :
            cls.Table [wrapped] = cls
            cls.singletons      = set (n.lower () for n in wrapped.singletons)
            cls.multi           = set (n.lower () for n in wrapped.multiple)
            cls.required        = set (n.lower () for n in wrapped.required)
            props_name          = cls.required.union (cls.multi)
            props_name          = props_name.union   (cls.singletons)
            cls.properties      = []
            for pn in props_name :
                cls.properties.append (pn)
                if pn in cls.multi :
                    prop = ICal_Multi_Prop (pn)
                else :
                    prop = ICal_Prop       (pn)
                setattr                    (cls, pn, prop)
    # end def __init__

# end class M_ICalendar

class _Component_ (TFL.Meta.Object) :
    """Root class for all icalendar component wrapper"""

    __metaclass__   = M_ICalendar
    wrapped         = None # needs to be set by all descendants
    Table           = {}

    def __init__ (self, * args, ** kw) :
        self._attributes = {}
        self.__super.__init__ ()
        self._icomp   = self._create_wrapped (* args, ** kw)
        self.children = []
        for c in self._icomp.subcomponents :
            if c.__class__ in self.Table :
                self.children.append (self.Table [c.__class__] (_icomp = c))
            else :
                self.children.append (c)
    # end def __init__

    def _create_wrapped (self, * args, ** kw) :
        if "_icomp" in kw :
            return kw ["_icomp"]
        return self.wrapped (* args, ** kw)
    # end def _create_wrapped

    def ical (self) :
        return self._icomp.ical ()
    # end def ical

    def diff (self, other) :
        result     = []
        undefined = ICal_Prop.undefined
        for p in self.properties :
            ps = getattr (self,  p, undefined)
            po = getattr (other, p, undefined)
            if ps != po :
                loc = "%s.%s" % (self.__class__.__name__, p)
                result.append ((loc, ps, po))
        for sc, oc in zip (self.children, other.children) :
            result.extend (sc.diff (oc))
        return result
    # end def diff

    name_length = 16

    def formatted (self, level = 0) :
        intent     = " " * level
        result     = []
        for p in self.properties :
            try :
                value = getattr (self, p)
                if p in self.multi :
                    value = \
                        ( "\n%s" % (" " * (3 + self.name_length + level))
                        ).join (str (v) for v in value)
                result.append \
                    ( "%s  %-*s = %s"
                    % (intent, self.name_length - level, p, value)
                    )
            except AttributeError :
                pass ### ignore not set properties
        children = []
        for c in self.children :
            text = c.formatted (level = level + 2)
            if text :
                children.append (text)
        if result or children :
            result.insert (0, "%s<%s>" % (intent, self.__class__.__name__))
            result.extend (children)
            result.append ("%s</%s>"   % (intent, self.__class__.__name__))
        return "\n".join (result)
    # end def formatted

    def __str__ (self) :
        return self.formatted ()
    # end def __str__

# end class _Component_

class Calendar (_Component_) :
    """Wrapper around the iCalenader.Calendar object"""

    wrapped         = icalendar.Calendar

    def _create_wrapped (self, filename = None, * args, ** kw) :
        if filename :
            return self.wrapped.from_string \
                (open (filename, "rb").read ())
        else :
            return self.__super._create_wrapped (* args, ** kw)
    # end def __init__

# end class Calendar

for ical_cls in \
        ( icalendar.cal.Component
        , icalendar.Event
        , icalendar.Alarm
        , icalendar.Timezone
        , icalendar.Todo
        , icalendar.Journal
        , icalendar.FreeBusy
        ) :
    type (_Component_) \
        ( ical_cls.__name__, (_Component_, )
        , dict
            ( wrapped     = ical_cls
            , __module__  = _Component_.__module__
            )
        )

def _main (cmd) :
    cal = Calendar (cmd.ical_file)
    print (cal)
    if cmd.ical_file_old :
        old = Calendar (cmd.ical_file_old)
        width = (17, 30, 30)
        format = " ".join ("%%-%ds" % (w, ) for w in width)
        sep    = " ".join ("~" * w for w in width)
        print ()
        print (format % ("WHERE", "OLD", "NEW"))
        print (sep)
        for where, new, old in cal.diff (old) :
            print (format % (where, old, new))
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "ical_file:S"
        , "ical_file_old:S"
        )
    , min_args      = 1
    , max_args      = 2
    )

if __name__ == "__main__" :
    _Command ()
### __END__ iCalendar
