# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer. All rights reserved
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
#    MOM.Meta.M_Pred_Type
#
# Purpose
#    Meta classes for MOM.Pred.Type classes
#
# Revision Dates
#     1-Oct-2009 (CT) Creation (factored from TOM.Meta.M_Pred_Type)
#    16-Apr-2012 (CT) Fix stylo
#    12-Aug-2012 (CT) Add `Unique`
#    12-Aug-2012 (CT) Use `_Export_Module`, DRY class names
#    11-Sep-2012 (CT) Change `Unique` to use `attr_none`, not `attributes`
#    29-Jan-2013 (CT) Force `Unique.kind` to `Uniqueness`, not `Region`
#    12-Jun-2013 (CT) Add `is_partial_p`
#    31-Jul-2013 (CT) Change `Unique.__init__` to set `error` to `None`
#    10-Oct-2014 (CT) Use `portable_repr`
#    21-Jun-2016 (CT) Replace map/lambda by list comprehension
#                     + Make `Quantifier` code Python-3 compatible:
#                       * Python-3 doesn't support argument unpacking for `def`
#                         and `lambda`
#                       * But it still supports item unpacking for loops and
#                         comprehensions
#                     + Factor `_set_code`
#    22-Jun-2016 (CT) Change `one_element_code` to return a `dict`
#    10-Aug-2016 (CT) Factor `Unique.Kind_Cls`
#    10-Aug-2016 (CT) Add `Exclude`
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL

from   _TFL.portable_repr    import portable_repr
from   _TFL.pyk              import pyk

import _MOM._Meta.M_Prop_Type

class _Condition_ (MOM.Meta.M_Prop_Type) :
    """Meta class for :mod:`~_MOM._Pred.Type` classes.

       `_Condition_` sets several class attributes needed by
       :class:`~_MOM._Pred.Kind.Kind`.

       `_Condition_` converts all properties listed in `_force_tuple` from
       strings to tuples.
    """

    _force_tuple = \
        ( "attributes"
        , "attr_none"
        , "bvar_attr"
        , "guard_attr"
        , "parameters"
        )

    def __new__ (meta, name, bases, dct) :
        for a in meta._force_tuple :
            if a in dct and isinstance (dct [a], pyk.string_types) :
                dct [a] = (dct [a], )
        dct.setdefault \
            ( "is_partial_p"
            , name.startswith ("_") and name.endswith ("_")
            )
        return meta.__mc_super.__new__ (meta, name, bases, dct)
    # end def __new__

# end class _Condition_

@pyk.adapt__str__
class Condition (_Condition_) :
    """Meta class for :class:`~_MOM._Pred.Type.Condition`

       `Condition` compiles `assertion` into `assert_code` and
       `guard` into `guard_code`.
    """

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        ### We must compile here even if `cls.assert_code` already exists.
        ### Otherwise overriding `assertion` would not work.
        ass = cls.assertion
        if ass:
            setattr (cls, "assert_code", compile (ass, ass, "eval"))
        guard = cls.guard
        if guard :
            if not getattr (cls, "guard_attr", None) :
                setattr (cls, "guard_attr", (guard, ))
            setattr (cls, "guard_code", compile (guard, guard, "eval"))
    # end def __init__

    def __str__  (cls) :
        return "%s : `%s'" % (cls.name, cls.assertion)
    # end def __str__

    def __repr__ (cls) :
        return "%s (%s, %s, %s)" % \
            ( cls.__class__.__name__
            , portable_repr (cls.attributes)
            , portable_repr (cls.assertion)
            , portable_repr (cls.parameters)
            )
    # end def __repr__

# end class Condition

@pyk.adapt__str__
class Quantifier (_Condition_) :
    """Meta class for quantifier predicates.

       `Quantifier` compiles several class attributes into code
       objects:

       .. attribute:: assert_code

         Compiled from `bvar` and `assertion`.

       .. attribute:: guard_code

         Compiled from `guard`, if any.

       .. attribute:: seq_code

         Compiled from `seq`

       .. attribute:: attr_code

         Compiled from `bvar` and `bvar_attr`, if any.
    """

    attr_code_fmt   = \
    assert_code_fmt = "list (%(code)s for %(bvar)s in seq)"

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if cls.bvar and cls.assertion :
            assert_code = cls.assert_code_fmt % dict \
                (bvar = cls.bvar, code = cls.assertion)
            cls._set_code ("assert_code", assert_code)
        guard = cls.guard
        if guard :
            if not getattr (cls, "guard_attr", None) :
                setattr (cls, "guard_attr", (guard, ))
            cls._set_code ("guard_code", guard)
        if isinstance (cls.seq, pyk.string_types) :
            cls._set_code ("seq_code", cls.seq)
        if cls.bvar and cls.bvar_attr :
            one_element_code = \
                ( "{%s}"
                % ( ", ".join (("%r : %s" % (bv, bv)) for bv in cls.bvar_attr)
                  )
                )
            attr_code = \
                ( cls.attr_code_fmt
                % dict (bvar = cls.bvar, code = one_element_code)
                )
            cls._set_code ("attr_code", attr_code)
    # end def __init__

    def _set_code (cls, name, code) :
        setattr (cls, name, compile (code, code, "eval"))
    # end def _set_code

    def __str__  (cls) :
        return "%s" % (cls.name, )
    # end def __str__

    def __repr__ (cls) :
        return '%s (%s, %s, %s, %s)' % \
            ( cls.__class__.__name__
            , portable_repr (cls.bvar)
            , portable_repr (cls.assertion)
            , portable_repr (cls.seq)
            , portable_repr (cls.description)
            )
    # end def __repr__

# end class Quantifier

class N_Quantifier (Quantifier) :
    """Meta class for :class:`~_MOM._Pred.Type.N_Quant`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if cls.lower_limit is not None and cls.upper_limit is None :
            setattr (cls, "upper_limit", cls.lower_limit)
    # end def __init__

# end class N_Quantifier

class U_Quantifier (Quantifier) :
    """Meta class for :class:`~_MOM._Pred.Type.U_Quant`"""

    assert_code_fmt = "list (not (%(code)s) for %(bvar)s in seq)"

# end class U_Quantifier

@pyk.adapt__str__
class Unique (_Condition_) :
    """Meta class for :class:`~_MOM._Pred.Type.Unique`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        KC = cls.Kind_Cls
        if cls.kind is None :
            cls.kind = KC
        elif cls.kind is not KC :
            raise TypeError \
                ( "%s predicate %s *must* have kind %s, not %s"
                % (KC.typ.title (), cls, KC.__name__, cls.kind)
                )
        if cls.attributes :
            raise TypeError \
                ( "%s predicate %s cannot define attributes, got %s"
                % (KC.typ.title (), cls, cls.attributes)
                )
        if cls.attr_none :
            from _MOM._Attr.Filter import Q
            setattr (cls, "aqs", tuple (getattr (Q, a) for a in cls.attr_none))
        cls.error = None
    # end def __init__

    @property
    def Kind_Cls (cls) :
        import _MOM._Pred.Kind
        return MOM.Pred.Uniqueness
    # end def Kind_Cls

    def __str__  (cls) :
        return "%s %s" % (cls.name, portable_repr (cls.attr_none))
    # end def __str__

    def __repr__ (cls) :
        return '%s predicate: %s' % (cls.kind.__name__, cls)
    # end def __repr__

# end class Unique

class Exclude (Unique) :
    """Meta class for :class:`~_MOM._Pred.Type.Exclude`"""

    @property
    def Kind_Cls (cls) :
        import _MOM._Pred.Kind
        return MOM.Pred.Exclusion
    # end def Kind_Cls

# end class Exclude

### «text» ### start of documentation
__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

.. autoclass:: _Condition_

"""

if __name__ != "__main__" :
    MOM.Meta._Export_Module ()
### __END__ MOM.Meta.M_Pred_Type
