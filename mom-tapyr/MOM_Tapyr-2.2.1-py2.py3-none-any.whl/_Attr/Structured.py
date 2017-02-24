# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Attr.Structured
#
# Purpose
#    Common base class for attributes with internal structure.
#
# Revision Dates
#    19-Jul-2016 (CT) Creation
#    20-Oct-2016 (CT) Add `iea_type_restrictions to `_SAT_Desc_`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

from   _MOM._Attr.Type       import *

import _MOM._Attr.Spec
import _MOM._Pred.Spec

from   _TFL.I18N             import _, _T

class _SAT_Desc_ (TFL.Meta.Object) :
    """Description of structured attribute type."""

    PNS                      = None
    app_type                 = None
    epk_sig                  = ()
    hash_sig                 = ()
    has_identity             = False
    iea_type_restrictions    = ()
    iea_type_restriction_map = {}
    is_partial               = False
    parents                  = ()
    relevant_root            = None
    sorted_by                = None
    spk_attr_name            = None
    spk_name                 = None

    @staticmethod
    def _saw_table_name (* args, ** kw) :
        pass ### No table here, move on
    # end def _saw_table_name

# end class _SAT_Desc_

class _M_Structured_ (MOM.Meta.M_Attr_Type.Root) :
    """Meta class for MOM.Attr._A_Structured_ classes."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        tn         = "%s__%s__type_desc" % (name, cls._i_rank)
        cls.E_Type = _SAT_Desc_.New \
            ( i_rank            = 1 << 24 + cls._i_rank
            , name_postfix      = name
            , type_base_name    = tn
            , type_name         = tn
            , _Attributes       = cls._Attributes
            , _Predicates       = cls._Predicates
            )
        cls._Attributes.m_setup_names (cls.E_Type, None)
        cls._Predicates.m_setup_names (cls.E_Type, None)
    # end def __init__

    def __call__ (cls, kind, e_type) :
        result             = cls.__m_super.__call__ (kind, e_type)
        E_Type             = result.E_Type
        E_Type.app_type    = e_type.app_type
        result._Attributes = result._Attributes (E_Type)
        result._Predicates = result._Predicates (E_Type)
        E_Type.sig_attr    = E_Type.user_attr
        return result
    # end def __call__

# end class _M_Structured_

class _A_Structured_ (TFL.Meta.BaM (A_Attr_Type, metaclass = _M_Structured_)) :
    """Common base class for attributes with internal structure."""

    Kind_Mixins         = (MOM.Attr._Structured_Mixin_, )

    class _Attributes (MOM.Attr.Spec) :
        """Spec of attributes defining internal structure."""

        ckd_name_eq_name = True

    # end class _Attributes

    class _Predicates (MOM.Pred.Spec) :
        """Spec of predicates applying to internal structure."""
    # end class _Predicates

# end class _A_Structured_

__sphinx__members = __all__ = __attr_types = attr_types_of_module ()

if __name__ != "__main__" :
    MOM.Attr._Export (* __all__)
### __END__ MOM.Attr.Structured
