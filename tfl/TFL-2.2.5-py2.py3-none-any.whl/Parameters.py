# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Parameters
#
# Purpose
#    Support scoped definition of parameters
#
# Revision Dates
#    11-Oct-2016 (CT) Creation (factor from GTW.Parameters)
#    17-Jan-2017 (CT) Factor `M_Definition._setup_prop`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL                       import TFL

from   _TFL._Meta.Property        import Lazy_Property
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.pyk                   import pyk
from   _TFL                       import sos

import _TFL._Meta.Object
import _TFL.Caller
import _TFL.Q_Exp

P = TFL.Q_Exp.Base (Ignore_Exception = AttributeError)

def ddict (* ds) :
    result = {}
    for d in ds :
        result.update (d)
    return result
# end def ddict

class _Parameter_ (TFL.Q_Exp.Q_Root) :

    def __init__ (self, * args, ** kw) :
        self.args = args
        self.kw   = kw
    # end def __init__

    def _resolved_args (self, P, args) :
        Q_Root = TFL.Q_Exp.Q_Root
        for a in args :
            if isinstance (a, Q_Root) :
                a = a (P)
            yield a
    # end def _resolved_args

    def _resolved_kw (self, P, kw) :
        Q_Root = TFL.Q_Exp.Q_Root
        for k, v in pyk.iteritems (kw) :
            if isinstance (v, Q_Root) :
                v = v (P)
            yield k, v
    # end def _resolved_kw

# end class _Parameter_

class P_dict (_Parameter_) :
    """Parameter dict: supports lazy evaluation of dict arguments."""

    def __call__ (self, P) :
        return dict \
            (  * tuple (self._resolved_args (P, self.args))
            , ** dict  (self._resolved_kw   (P, self.kw))
            )
    # end def __call__

# end class P_dict

class M_Definition (TFL.Meta.Object.__class__) :
    """Meta class for `Definition`."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        bn = tuple (reversed ([getattr (b, "_nested_", {}) for b in bases]))
        cls._nested_ = _nested_ = ddict (* bn)
        Q_Root = TFL.Q_Exp.Q_Root
        for k, v in pyk.iteritems (dct) :
            cls._setup_prop (k, v, Q_Root, _nested_)
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        result = cls.__m_super.__call__ (* args, ** kw)
        for k, v in pyk.iteritems (cls._nested_) :
            setattr (result, k, v (R = result))
        return result
    # end def __call__

    def _setup_prop (cls, k, v, Q_Root, _nested_) :
        if isinstance (v, Q_Root) :
            setattr (cls, k, Lazy_Property (k, v))
        elif isinstance (v, M_Definition) :
            _nested_ [k] = v
    # end def _setup_prop

# end class M_Definition

class Definition (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Definition)) :
    """Definition of parameters for media, i.e., CSS and JS, fragments.

    >>> from _TFL.portable_repr  import portable_repr

    >>> class Defaults (Definition) :
    ...   foo = 1
    ...   bar = P.foo * 2
    ...   class nav_col (Definition) :
    ...     bar = 42
    ...     baz = 0
    ...     class own_links (Definition) :
    ...       qux = P.R.bar * 2
    ...       quy = P.T.bar * 2
    ...       quz = P.T.foo * 0.5
    ...     spec = P_dict (a = P.bar, border = "solid")
    ...
    >>> class App (Defaults) :
    ...   foo = 2
    ...   class nav_col (Defaults.nav_col) :
    ...     bar = 137
    ...
    >>> D = Defaults ()
    >>> E = App ()
    >>> D.foo, E.foo
    (1, 2)
    >>> D.bar, E.bar
    (2, 4)
    >>> D.nav_col.own_links.qux, E.nav_col.own_links.qux
    (84, 274)
    >>> D.nav_col.own_links.quy, E.nav_col.own_links.quy
    (4, 8)
    >>> D.nav_col.own_links.quz, E.nav_col.own_links.quz
    (0.5, 1.0)
    >>> print (portable_repr (D.nav_col.spec), portable_repr (E.nav_col.spec))
    {'a' : 42, 'border' : 'solid'} {'a' : 137, 'border' : 'solid'}

    """

    def __init__ (self, R = None) :
        self.R = R
    # end def __init__

    @Once_Property
    def T (self) :
        R = self.R
        if R is not None :
            return R.T
        else :
            return self
    # end def T

# end class Definition

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Parameters
