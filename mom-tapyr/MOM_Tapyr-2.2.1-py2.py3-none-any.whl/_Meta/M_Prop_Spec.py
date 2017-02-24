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
#    MOM.Meta.M_Prop_Spec
#
# Purpose
#    Root meta class for for attribute-spec and predicate-spec metaclasses
#
# Revision Dates
#    29-Sep-2009 (CT) Creation (factored from TOM.Meta.M_Prop_Spec)
#    26-Nov-2009 (CT) `_m_add_prop` added
#    23-Mar-2010 (CT) Remove names in `renameds` from `_names`
#     9-Apr-2010 (CT) `m_setup_names` changed to ignore attributes set to `None`
#    12-Sep-2012 (CT) Add support for `dyn_doc_p`
#    12-Jun-2013 (CT) Use `is_partial_p`
#    12-Jun-2013 (CT) Add argument `app_type` to `m_setup_names`
#    12-Jun-2013 (CT) Set `DET`, `DET_Base`, and `DET_Root` in `m_setup_names`
#    10-Mar-2014 (CT) Add new entries in `.auto_up_depends` to `_own_names`
#    10-Mar-2014 (CT) Set `_d_rank` in `m_setup_names`
#    11-Mar-2014 (CT) Add support for `_Overrides`
#    26-Jan-2015 (CT) Derive from `M_Auto_Update_Combined`, not `M_Class`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals, print_function

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

import _TFL._Meta.M_Auto_Update_Combined
import _MOM._Meta.M_Prop_Type

class M_Prop_Spec (TFL.Meta.M_Auto_Update_Combined) :
    """Root meta class for for attribute-spec and predicate-spec metaclasses.

       `MOM.Meta.M_Prop_Spec` provides the meta machinery for defining
       :class:`attribute<_MOM._Meta.M_Attr_Spec.M_Attr_Spec>` and
       :class:`predicate<_MOM._Meta.M_Pred_Spec.M_Pred_Spec>` specifications.

       `M_Prop_Spec` gathers all class attributes of the `Spec` which are
       derived from the :class:`base property
       type<_MOM._Meta.M_Prop_Type.M_Prop_Type>` and puts them into the class
       attributes mapping property names to property values:

       .. attribute:: _names

         Dictionary with all locally defined *and* all inherited properties.

       .. attribute:: _own_names

         Dictionary with all locally defined properties.

       Setting a class variable to `None` in a derived `Spec` will remove the
       property from the `Spec`.
    """

    _attrs_uniq_to_update_combine = ("Kind_Mixins", )
    _Overridden                   = set ()

    def m_setup_names (cls, e_type, app_type = None) :
        dct        = dict (cls.__dict__)
        _names     = {}
        _own_names = {}
        setattr (cls, "_names",     _names)
        setattr (cls, "_own_names", _own_names)
        for b in reversed (cls.__bases__) :
            _names.update (getattr (b, "_names", {}))
        _own_names.update \
            (  (n, v)
            for n, v in pyk.iteritems (_names) if v and v.dyn_doc_p
            )
        Overrides = dct.get ("_Overrides")
        if Overrides and cls not in cls._Overridden :
            cls._Overridden.add (cls)
            for k, o in pyk.iteritems (Overrides) :
                try :
                    p = getattr (cls, k)
                except KeyError :
                    raise MOM.Error.Inconsistent_Attribute \
                        ( "%s %s: Attribute `%s = %r` has no parent"
                        % (dct ["__module__"], e_type, k, o)
                        )
                if isinstance (p, MOM.Meta.M_Prop_Type) :
                    d = dct [k] = p.__class__ \
                        ( k, (p, ), dict (o, __module__ = cls.__module__))
                    setattr (cls, k, d)
        auto_up_depends = set ()
        for n, v in pyk.iteritems (dct) :
            if getattr (v, "is_partial_p", True) or n == "_Overrides" :
                continue
            if v is None :
                _names [n] = _own_names [n] = None
            elif isinstance (v, MOM.Meta.M_Prop_Type) :
                auto_up_depends.update (getattr (v, "auto_up_depends", ()))
                if getattr (v, "_d_rank",  None) is None :
                    v._d_rank = v._i_rank
                if app_type :
                    if v.DET_Root is None :
                        v.DET_Root = e_type.type_name
                    else :
                        v.DET_Base = v.DET
                    v.DET = e_type.type_name
                _names [n] = _own_names [n] = v
                for bn in v.renameds :
                    try :
                        del _names [bn]
                    except KeyError :
                        print (cls, v, n, bn)
                        raise
            elif n in _names :
                raise cls._m_inconsistent_prop (n, v, _names, dct)
        if auto_up_depends :
            ### new or redefined attributes reference inherited attributes
            ### --> include the inherited attributes in `_own_names`
            ###     * otherwise, `dependent_attrs` of the inherited
            ###       attributes points to redefined attributes
            _own_names.update \
                (   (n, _names [n])
                for n in auto_up_depends if n not in _own_names
                )
    # end def m_setup_names

    def _m_add_prop (cls, e_type, name, prop_type) :
        cls._names [name] = cls._own_names [name] = prop_type
        setattr (cls, name, prop_type)
        return prop_type
    # end def _m_add_prop

# end class M_Prop_Spec

### «text» ### start of documentation
__doc__ = """

"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*")
### __END__ MOM.Meta.M_Prop_Spec
