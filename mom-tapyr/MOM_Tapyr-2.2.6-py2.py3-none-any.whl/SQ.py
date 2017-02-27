# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.SQ
#
# Purpose
#    Symbolic query expressions for MOM meta object model
#
# Revision Dates
#    10-Jul-2013 (CT) Creation
#    13-Aug-2015 (CT) Add module docstring, improve class docstrings
#    13-Aug-2015 (CT) Add support for Q-get-expressions to `_SQ_.__getitem__`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

from   _TFL.I18N             import _, _T

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL._Meta.Property
import _TFL.Decorator
import _TFL.Q_Exp
import _TFL.Q_Result

from   _MOM._Attr.Filter     import Q

@pyk.adapt__str__
class _SQ_ (TFL.Meta.Object) :
    """Symbolic query generator.

       Each symbolic query starts with the selection of an essential type to
       query, for instance::

           sq_property = SQ [Q.PAP.Property]

           sq_person   = SQ [Q.PAP.Person]

       ``sq_person`` is a symbolic query for a non-partial type, `sq_property`
       defines a polymorphic symbolic query over a set of types derived from
       the partial  type ``PAP.Property``.

       ``SQ [Q.PNS.Type]`` returns an instance of :class:`_E_Type_`.
    """

    _Table = {}

    def __getitem__ (self, key) :
        if isinstance (key, TFL.Q_Exp._Get_) :
            key = key._name
        try :
            result = self._Table [key]
        except KeyError :
            result = self._Table [key] = self._E_Type_ (key)
        return result
    # end def __getitem__

    def __str__ (self) :
        return "SQ"
    # end def __str__

# end class _SQ_

@TFL.Add_New_Method (_SQ_)
@pyk.adapt__str__
class _E_Type_ (TFL.Meta.Object) :
    """Symbolic query for a specific E_Type.

       Each instance of :class:`_E_Type_` is bound to a specific essential
       type. One can refine a symbolic query by applying any of the various
       methods, e.g., :meth:`filter`.
    """

    _attr      = None
    _attrs     = ()
    _distinct  = None
    _filters   = ()
    _group_by  = ()
    _kw        = {}
    _limit     = None
    _offset    = None
    _order_by  = ()
    _strict    = False

    def _q_refiner (f) :
        name = f.__name__
        qr_f = getattr (TFL._Q_Result_, name, None)
        if qr_f is not None and not f.__doc__ :
            f.__doc__ = qr_f.__doc__
        return f
    # end def _q_refiner

    def __init__ (self, t) :
        self.type_name = getattr (t, "type_name", t)
    # end def __init__

    def __call__ (self, q) :
        """Apply symbolic query to `q`.

           `q` can be one of:

           * an instance of :class:`~_MOM.Scope.Scope`

           * an instance of :class:`E_Type_Manager<_MOM.E_Type_Manager.Entity>`

           * the result of a call to
             :meth:`~_MOM.E_Type_Manager.Entity.query`

                 In this case, the query refinements of `self` are applied to
                 `q`.

           In any case, the symbolically defined query operations of `self` are
           applied to the query resulting from `q`.
        """
        if isinstance (q, MOM.Scope) :
            q = q [self.type_name]
        if isinstance (q, MOM.E_Type_Manager.Entity) :
            result = q.query (strict = self._strict)
        else :
            result = q
        if self._filters or self._kw :
            result = result.filter   (* self._filters, ** self._kw)
        if self._group_by :
            result = result.group_by (* self._group_by)
        if self._distinct is not None :
            result = result.distinct (self._distinct)
        for c in self._order_by :
            result = result.order_by (c)
        if self._limit is not None :
            result = result.limit    (self._limit)
        if self._offset is not None :
            result = result.offset   (self._offset)
        if self._attr is not None :
            result = result.attr     (self._attr)
        if self._attrs :
            result = result.attrs    (self._attrs)
        return result
    # end def __call__

    def apply (self, q) :
        return self (q)
    # end def apply

    apply.__doc__ = __call__.__doc__

    @_q_refiner
    def attr (self, getter) :
        return self._clone (_attr = getter)
    # end def attr

    @_q_refiner
    def attrs (self, * getters) :
        return self._clone (_attrs = getters)
    # end def attrs

    @_q_refiner
    def distinct (self, value = True) :
        return self._clone (_distinct = value)
    # end def distinct

    @_q_refiner
    def filter (self, * criteria, ** kw) :
        self._strict = kw.pop ("strict", False)
        sk           = kw.pop ("sort_key", ())
        return self._clone \
            ( _filters  = self._filters + criteria
            , _kw       = dict (self._kw, ** kw)
            , _order_by = self._order_by + ((sk, ) if sk else ())
            )
    # end def filter

    @_q_refiner
    def group_by (self, * columns) :
        return self._clone (_group_by = self._group_by + columns)
    # end def group_by

    @_q_refiner
    def limit (self, limit) :
        return self._clone (_limit = limit)
    # end def limit

    @_q_refiner
    def offset (self, offset) :
        return self._clone (_offset = offset)
    # end def offset

    @_q_refiner
    def order_by (self, * criteria) :
        return self._clone (_order_by = self._order_by + criteria)
    # end def order_by

    def _clone (self, ** kw) :
        cls    = self.__class__
        result = cls.__new__   (cls)
        result.__dict__.update (self.__dict__, ** kw)
        return result
    # end def _clone

    def __str__ (self) :
        result = ["SQ [%s]" % (self.type_name)]
        if self._filters or self._kw :
            args = list (str (f) for f in self._filters)
            args.extend \
                (   "%s = %r" % (k, v)
                for k, v in sorted (pyk.iteritems (self._kw))
                )
            result.append ("filter (%s)" % ", ".join (args))
        if self._group_by :
            args = list (str (f) for f in self._group_by)
            result.append ("group_by (%s)" % ", ".join (args))
        if self._distinct is not None :
            result.append ("distinct (%s)" % self._distinct)
        if self._order_by :
            args = list (str (f) for f in self._order_by)
            result.append ("order_by (%s)" % ", ".join (args))
        if self._limit is not None :
            result.append ("limit (%s)" % (self._limit, ))
        if self._offset is not None :
            result.append ("limit (%s)" % (self._offset, ))
        if self._attr is not None :
            result.append ("attr (%s)" % (self._attr, ))
        if self._attrs :
            result.append ("attrs (%s)" % (self._attrs, ))
        sep = "\n    ." if len (result) > 2 else "."
        return sep.join (result)
    # end def __str__

# end class _E_Type_

SQ = _SQ_ ()

### «text» ### start of documentation
__doc__ = r"""
This module implements a symbolic query language. It exports the symbolic query
generator instance :obj:`SQ` which is used to define symbolic queries.

A symbolic query generated by :obj:`SQ` is a Python callable:
applying a SQ instance to a :class:`scope<_MOM.Scope.Scope>`,
:class:`E_Type_Manager<_MOM.E_Type_Manager.Entity>`, or
:meth:`query result<_MOM.E_Type_Manager.Entity.query>`
applies the symbolic query for that scope/manager/query
and returns the resulting query result.

.. data:: SQ

    `SQ` is an instance of :class:`_SQ_`.

    >>> sq = SQ ["PAP.Person"]
    >>> print (sq)
    SQ [PAP.Person]
    >>> print (sq.order_by (- Q.last_name))
    SQ [PAP.Person].order_by (- Q.last_name)
    >>> print (sq.order_by (- Q.last_name).limit (5).offset (10))
    SQ [PAP.Person]
        .order_by (- Q.last_name)
        .limit (5)
        .limit (10)
    >>> print (sq.filter (Q.last_name.STARTSWITH ("tanzer")))
    SQ [PAP.Person].filter (Q.last_name.startswith ('tanzer',))
    >>> print (sq)
    SQ [PAP.Person]
    >>> SQ [Q.PAP.Person] is sq
    True
    >>> sq.order_by (- Q.last_name) is sq
    False
    >>> SQ [Q.PAP.Person_has_Phone] is sq
    False

"""

if __name__ != "__main__" :
    MOM._Export ("SQ")
### __END__ MOM.SQ
