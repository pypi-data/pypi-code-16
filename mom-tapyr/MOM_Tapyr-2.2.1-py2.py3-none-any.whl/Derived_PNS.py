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
#    MOM.Derived_PNS
#
# Purpose
#    Package_Namespace derived from the `MOM` package namespace
#
# Revision Dates
#    15-Jun-2013 (CT) Creation
#    17-Jun-2013 (CT) Add `_MOM_Link_n_` to `MOM_bases`, `MOM_base_parents`
#    13-Aug-2015 (CT) Add module docstring, improve class docstrings
#    14-Aug-2015 (CT) Change `_Lazy_Resolver_._derived` to set `immaterial`
#    ««revision-date»»···
#--

from   __future__             import division, print_function
from   __future__             import absolute_import, unicode_literals

from   _MOM                   import MOM
from   _TFL                   import TFL

from   _TFL.Package_Namespace import \
     Derived_Package_Namespace, Package_Namespace
from   _TFL.pyk               import pyk
from   _TFL.Regexp            import Regexp, re

import _MOM.Entity
import _MOM.Link
import _MOM.Object

import _TFL._Meta.M_Class
import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Caller

_doc_pat = Regexp (r"\s+ of \s+ ([A-Za-z0-9_.]+)$", re.VERBOSE)

class _Lazy_Resolver_ (TFL.Meta.Object) :
    """Lazy resolver for PNS-specific base classes derived from their
       corresponding base classes in the parent PNS (default: MOM).
    """

    _MOM_bases        = None
    _MOM_base_parents = None

    def __init__ (self, PNS, parent_PNS, module_name) :
        self.PNS         = PNS
        self.parent_PNS  = parent_PNS
        self.module_name = module_name
        ### trigger computation of `MOM_bases` here to limit to real MOM base
        ### types (we don't want to auto-derive descendents of MOM.An_Entity)
        self.MOM_bases
    # end def __init__

    def __call__ (self, PNS, name) :
        if name not in self.MOM_bases :
            raise AttributeError (name)
        try :
            parent_PNS = self.parent_PNS
            base       = getattr (parent_PNS, name)
            mixin_name = self.MOM_base_parents [name]
            mixin      = getattr (PNS, mixin_name) if mixin_name else None
            return self._derived (PNS, self.postfix, base, mixin)
        except AttributeError as exc :
            ### Raise `RuntimeError` here to avoid hiding of an error that
            ### should not be hidden
            ### * `Derived_Package_Namespace.__getattr__` delegates to
            ###   `parent_PNS` in case of an `AttributeError`
            raise RuntimeError (exc)
    # end def __call__

    @property
    def MOM_base_parents (self) :
        result = self._MOM_base_parents
        if result is None :
            def _gen () :
                for bn, cls in pyk.iteritems (self.MOM_bases) :
                    if cls.parents :
                        cls = cls.parents [0]
                        pbn = cls.type_base_name
                        yield bn, pbn
                    else :
                        yield bn, None
            result = self.__class__._MOM_base_parents = dict (_gen ())
        return result
    # end def MOM_base_parents

    @property
    def MOM_bases (self) :
        result = self._MOM_bases
        if result is None :
            def _gen () :
                for b in MOM.Entity._S_Extension :
                    tbn = b.type_base_name
                    if b.type_name.startswith ("MOM.") :
                        yield tbn, b
                    else :
                        break
            result = self.__class__._MOM_bases = dict (_gen ())
        return result
    # end def MOM_bases

    @TFL.Meta.Once_Property
    def postfix (self) :
        return "_" + self.PNS._._bname
    # end def postfix

    def _derived (self, PNS, postfix, base, mixin = None, ** kw) :
        name   = base.type_base_name
        result = base.New \
            ( name_postfix  = postfix
            , _real_name    = name
            , head_mixins   = (mixin, ) if mixin else ()
            , immaterial    = True
            , is_partial    = True
            , PNS           = PNS
            , __doc__       = _doc_pat.sub
                (" of %s." % (PNS.__name__), base.__doc__)
            , __module__    = self.module_name
            , ** kw
            )
        return result
    # end def _derived

# end class _Lazy_Resolver_

class Derived_PNS \
          ( TFL.Meta.BaM
              (Derived_Package_Namespace, metaclass = TFL.Meta.M_Class)
          ) :
    """Package_Namespace derived from the :mod:`MOM<_MOM>` package namespace
       with a lazy resolver for derived base classes like `Entity`,
       `Id_Entity`, `Object`, `Link1`, etc.

       `Derived_PNS` is typically used for partial object models.
    """

    def __init__ (self, * lazy_resolvers, ** kw) :
        parent                     = kw.pop ("parent",    MOM)
        pns_alias                  = kw.pop ("pns_alias", None)
        c_scope, module_name, name = self._args_from_kw (kw)
        base_resolver              = _Lazy_Resolver_ (self, parent, module_name)
        self.__super.__init__ \
            ( parent, base_resolver
            , module_name = module_name
            , name        = name
            , c_scope     = c_scope
            , * lazy_resolvers
            , ** kw
            )
        if pns_alias :
            qn = self.__name__
            if qn not in MOM.Entity.PNS_Aliases :
                MOM.Entity.m_add_PNS_Alias (pns_alias, self)
    # end def __init__

# end class Derived_PNS

class Underived_PNS \
          (TFL.Meta.BaM (Package_Namespace, metaclass = TFL.Meta.M_Class)) :
    """Package_Namespace based on, but not derived from, from the
       :mod:`MOM<_MOM>` package namespace with a lazy resolver for derived base
       classes like `Entity`, `Id_Entity`, `Object`, `Link1`, etc.

       `Underived_PNS` is typically used for the top-level
       application-specific object model.
    """

    def __init__ (self, * lazy_resolvers, ** kw) :
        pns_alias                  = kw.pop ("pns_alias", None)
        c_scope, module_name, name = self._args_from_kw (kw)
        base_resolver              = _Lazy_Resolver_ (self, MOM, module_name)
        self.__super.__init__ \
            ( base_resolver
            , module_name = module_name
            , name        = name
            , c_scope     = c_scope
            , * lazy_resolvers
            , ** kw
            )
        if pns_alias :
            qn = self.__name__
            if qn not in MOM.Entity.PNS_Aliases :
                MOM.Entity.m_add_PNS_Alias (pns_alias, self)
    # end def __init__

# end class Underived_PNS

### «text» ### start of documentation
__doc__ = r"""
This module provides the classes :class:`Derived_PNS` and
:class:`Underived_PNS` to define :class:`package
namespace<_TFL.Package_Namespace.Package_Namespace>` instances, called PNS,
for MOM object models. `Derived_PNS` and `Underived_PNS` will automatically
derive PNS-specific sub-classes with the correct
attr:`~_MOM.Entity.Id_Entity.PNS` value for classes like `PNS.Id_Entity`,
`PNS.Object`, and `PNS.Link2`.

"""

if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.Derived_PNS
