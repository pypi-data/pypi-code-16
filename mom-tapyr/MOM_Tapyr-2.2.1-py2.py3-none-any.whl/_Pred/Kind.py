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
#    MOM.Pred.Kind
#
# Purpose
#    Provide property classes for various predicate kinds
#
# Revision Dates
#    24-Sep-2009 (CT) Creation (factored from TOM.Pred.Kind)
#    25-Feb-2010 (CT) `check_pred_p` added (honoring `check_always`)
#    11-Mar-2010 (CT) `check_pred_p` removed (was a Bad Idea (tm))
#     2-Sep-2010 (CT) `Region` added
#    27-Apr-2012 (CT) Add `Region` to last paragraph of `__doc__`
#    12-Sep-2012 (CT) Add `__init__` argument `e_type`
#    29-Jan-2013 (CT) Add `Uniqueness`
#    30-Jan-2013 (CT) Add `Kind.__repr__`
#     5-May-2016 (CT) Add `Object_Init`, factor `_Object_`
#    10-Aug-2016 (CT) Add `Exclusion`
#    ««revision-date»»···
#--

from   _TFL                  import TFL
from   _MOM                  import MOM

import _TFL._Meta.Property

import _MOM._Pred
import _MOM._Prop.Kind

class Kind (MOM.Prop.Kind) :
    """Root class of predicate kinds to used as properties for essential
       predicates of the MOM meta object model.
    """

    kind                  = None ### override in descendents
    pred                  = None
    prop                  = TFL.Meta.Alias_Property ("pred")
    Table                 = dict ()

    def __init__ (self, pred_type, e_type) :
        self.__super.__init__ (pred_type, e_type)
        self.attrs = set      (pred_type.attributes + pred_type.attr_none)
    # end def __init__

    def get_attr_value (self, obj, attr) :
        return getattr (obj, attr, None)
    # end def get_attr_value

    def check_predicate (self, obj, attr_dict = {}) :
        return self.pred (self, obj, attr_dict)
    # end def check_predicate

    _del = None
    _get = check_predicate
    _set = None

    def __repr__ (self) :
        return repr (self.pred)
    # end def __repr__

# end class Kind

class Exclusion (Kind) :
    """Predicate kind for exclusion invariant.

       Exclusion predicates must be satisfied before an object can be
       added to the database.

       Exclusion predicates are checked by `scope.add` before attempting to
       actually add the entity. Some backends might move the checks of
       some exclusion predicates to the database engine.
    """

    kind = "exclusion"
    typ  = "exclusive"

# end class Exclusion

class _Object_ (Kind) :
    """Base class for predicate kinds for object-local invariants."""

    def __init__ (self, pred_type, e_type) :
        self.__super.__init__ (pred_type, e_type)
        assert "is_used" not in self.pred.guard_attr, \
            ( "System-dependent attribute `is_used` can't be used in guard "
              "of %s invariant %s!"
            % (self.name, self.kind)
            )
    # end def __init__

# end class _Object_

class Object (_Object_) :
    """Predicate kind for object-local invariant.

       Object predicates must be satisfied at all times. They can only refer
       to attributes of a single instance of the essential class or
       association for which the predicate is defined.

       Object predicates are checked whenever the value of one or more
       essential attributes is set or changed.
    """

    kind = "object"

    def get_attr_value (self, obj, attr) :
        ### Don't want computed values here because they might
        ### refer to attribute values about to be changed (and thus
        ### trigger spurious predicate violations in `obj.set`)
        ### This is only a problem for object predicates, since they're the
        ### only ones that get automatically evaluated on a set operation
        if obj.raw_attr (attr) is not "" :
            return self.__super.get_attr_value (obj, attr)
    # end def get_attr_value

# end class Object

class Object_Init (_Object_) :
    """Predicate kind for object_init invariant.

       Object-init predicates must be satisfied at the time of object creation.
       They can only refer to attributes of a single instance of the essential
       class or association for which the predicate is defined.

       Object-init predicates are checked before the object is created.
    """

    kind = "object_init"

# end class Object_Init

class Region (Kind) :
    """Predicate kind for region-wide invariant.

       Region predicates can refer to other objects and their predicates and
       must be satisfied before an object can be committed to the database.

       Region predicates are checked by `scope.commit` before attempting to
       actually do the commit. Some backends might move the checks of
       some regional predicates to the database engine.
    """

    kind = "region"

# end class Region

class System (Kind) :
    """Predicate kind for system-wide invariant.

       System predicates can refer to other objects and their predicates and
       must *not* be satisfied at all times.

       Many applications require that all system predicates are satisfied
       before some commands can be performed.
    """

    kind = "system"

# end class System

class Uniqueness (Kind) :
    """Predicate kind for uniqueness invariant.

       Uniqueness predicates must be satisfied before an object can be
       added to the database.

       Uniqueness predicates are checked by `scope.add` before attempting to
       actually add the entity. Some backends might move the checks of
       some uniqueness predicates to the database engine.
    """

    kind = "uniqueness"
    typ  = "unique"

# end class Uniqueness

### «text» ### start of documentation
__doc__ = """

    :class:`Kind` is the root class of a hierarchy of classes defining the
    various kinds of predicates of essential classes. The predicate kind
    controls how a predicate is evaluated. Technically, `Kind` and its
    subclasses define Python `property` types.

    The kind of a concrete predicate is specified as one the properties of
    the :mod:`predicate's type<_MOM._Pred.Type>`. The kind
    class gets instantiated by :class:`~_MOM._Pred.Spec.Spec` which passes
    the `type` to the kind's `__init__`.

    This module provides five kinds of predicates: :class:`Object`,
    :class:`Object_Init`, :class:`Region`, :class:`System`, and
    :class:`Uniqueness`. A specific application or application domain can
    define additional kinds of predicates by providing additional classes
    derived from :class:`Kind`.


"""

if __name__ != "__main__" :
    MOM.Pred._Export ("*")
### __END__ MOM.Pred.Kind
