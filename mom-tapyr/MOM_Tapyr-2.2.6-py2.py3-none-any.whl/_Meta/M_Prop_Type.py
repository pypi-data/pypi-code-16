# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Meta.M_Prop_Type
#
# Purpose
#    Base meta class for metaclasses for MOM.Attr.Type and MOM.Pred.Type
#
# Revision Dates
#    28-Sep-2009 (CT) Creation  (factored from TOM.Meta.M_Prop_Type)
#     5-Jan-2010 (CT) Use `TFL._Meta.M_Auto_Combine` as base class
#    12-Sep-2012 (CT) Add `dyn_doc_p`
#     4-Jun-2013 (CT) Try to take start value of `dyn_doc_p` from `dct`
#    14-Jun-2013 (CT) Change `dyn_doc_p` to dict
#    14-Jun-2013 (CT) Use `_doc_properties` in `__init__`, not literal in
#                     `__new__`  to normalize indent, update `dyn_doc_p`
#    10-Mar-2014 (CT) Improve grep-ability of `dyn_doc_p` update
#    10-Mar-2014 (CT) Factor `_i_rank` in here
#    26-Mar-2014 (CT) Add guard against double quotes in `_doc_properties`
#    26-Jan-2015 (CT) Use `M_Auto_Update_Combined`, not `M_Auto_Combine_Dict`,
#                     as ancestor
#     9-Dec-2015 (CT) Add `_Doc_Map_`, `_M_Doc_Map_`
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._Meta
import _TFL._Meta.M_Auto_Combine_Nested_Classes
import _TFL._Meta.M_Auto_Update_Combined
import _TFL._Meta.Once_Property

import _TFL.normalized_indent
from   _TFL.predicate        import first
from   _TFL.pyk              import pyk

class _M_Doc_Map_ (TFL.Meta.M_Class) :
    """Meta class for `_Doc_Map_` classes."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        _own_names = set (k for k in dct if not k.startswith ("__"))
        _names     = set (_own_names)
        for b in cls.__bases__ :
            _names.update (getattr (b, "_names", ()))
        for k in _own_names :
            v = dct [k]
            if v :
                v = TFL.normalized_indent (v)
                setattr (cls, k, v)
        setattr (cls, "_names",     _names)
        setattr (cls, "_own_names", _own_names)
        if not cls.__doc__ :
            setattr \
                ( cls, "__doc__"
                , first (b.__doc__ for b in cls.__bases__ if b.__doc__)
                )
        cls._OWN = cls._ALL = None
    # end def __init__

    @property
    def ALL (cls) :
        """All documented attributes of `cls` and its ancestors."""
        result = cls._ALL
        if result is None :
            result = cls._ALL = cls._items (cls._names)
        return result
    # end def ALL

    @property
    def OWN (cls) :
        """Documented attributes of `cls` itself."""
        result = cls._OWN
        if result is None :
            result = cls._OWN = cls._items (cls._own_names)
        return result
    # end def OWN

    def get (self, key, default) :
        try :
            return getattr (cls, key)
        except AttributeError :
            return default
    # end def get

    def _items (cls, names) :
        def _gen (cls, names) :
            for k in sorted (names) :
                v = getattr (cls, k)
                if v :
                    yield k, v
        return list (_gen (cls, names))
    # end def _items

    def __getitem__ (cls, key) :
        try :
            return getattr (cls, key)
        except AttributeError :
            raise KeyError (key)
    # end def __getitem__

    def __iter__ (cls) :
        return iter (cls._names)
    # end def __iter__

# end class _M_Doc_Map_

class M_Prop_Type \
        ( TFL.Meta.M_Auto_Update_Combined
        , TFL.Meta.M_Auto_Combine_Nested_Classes
        ) :
    """Root of metaclasses for MOM.Attr.Type and MOM.Pred.Type"""

    count                      = 0

    _nested_classes_to_combine = ("_Doc_Map_", )

    def __new__ (meta, name, bases, dct) :
        doc = dct.get ("__doc__")
        if not doc :
            if "__doc__" in dct :
                del dct ["__doc__"]
        elif "description" not in dct :
            dct ["description"] = doc
        dct ["name"] = name
        return meta.__mc_super.__new__ (meta, name, bases, dct)
    # end def __new__

    def __init__ (cls, name, bases, dct) :
        M_Prop_Type.count += 1
        cls._i_rank        = M_Prop_Type.count
        cls.__m_super.__init__ (name, bases, dct)
        cls.dyn_doc_p = dyn_doc_p = dict (getattr (cls, "dyn_doc_p", {}))
        for n in cls._doc_properties :
            v = dct.get (n)
            if v :
                v = TFL.normalized_indent (v)
                setattr (cls, n, v)
                if "%(" in v :
                    dyn_doc_p [n] = v
                if '"' in v :
                    ### Double quotes in _doc_properties break generated HTML
                    ### like::
                    ###     """<input title="%s" ···>""" % (v, )
                    raise TypeError \
                        ( "Property `%s` of %s must not contain double quotes"
                        % (n, cls)
                        )
        if not cls.__doc__ :
            cls.__doc__ = cls.description
    # end def __init__

# end class M_Prop_Type

### «text» ### start of documentation
__doc__ = """

    `MOM.Meta.M_Prop_Type` provides the meta machinery for defining
    :class:`attribute<_MOM._Meta.M_Attr_Type.Root>` and
    :class:`predicate<_MOM._Meta.M_Pred_Type.M_Pred_Type>` types.

    `M_Prop_Type` adds the class attributes:

    .. attribute:: name

      The name of the property.

    `M_Prop_Type` normalizes the `__doc__`, `description` and `explanation`
    attributes:

    * It removes an empty `__doc__` attribute to allow inheritance (by
      default, each Python class gets an empty `__doc__` attribute if the
      class definition doesn't contain an explicit docstring).

    * It sets `description` to the value of `__doc__`, if the class
      definition contains an explicit docstring.

    * It normalizes the indentation of `description` and `explanation` by
      calling `TFL.normalized_indent`.

"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*","_M_Doc_Map_")
### __END__ MOM.Meta.M_Prop_Type
