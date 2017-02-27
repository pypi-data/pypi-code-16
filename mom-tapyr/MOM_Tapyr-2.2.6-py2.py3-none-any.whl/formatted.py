# -*- coding: utf-8 -*-
# Copyright (C) 2014 Mag. Christian Tanzer All rights reserved
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
#    MOM.formatted
#
# Purpose
#    Format MOM entity for display
#
# Revision Dates
#    16-Jan-2014 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL

import _MOM.import_MOM
from   _MOM._Attr                 import Selector

from   _TFL._Meta.Single_Dispatch import Single_Dispatch

@Single_Dispatch (T = MOM.Attr.Kind)
def formatted_attr (ak, obj, AQ, level, indent, skip_attrs) :
    l = 24 - len (indent * level)
    return "%-*s : %s" % (l, ak.ui_name_T, getattr (obj.FO, ak.name))
# end def formatted_attr

@formatted_attr.add_type (MOM.Attr._EPK_Mixin_)
def _formatted_attr_epk (ak, obj, AQ, level, indent, skip_attrs) :
    ao = ak.get_value (obj)
    if ao is not None :
        return formatted \
            (ao, AQ, level, indent, skip_attrs, _ui_name = ak.ui_name_T)
# end def _formatted_attr_epk

def formatted \
        ( obj, AQ = None, level = 1, indent = "  ", skip_attrs = {}
        , _ui_name = None
        ) :
    return "\n".join \
        (formatted_iter (obj, AQ, level, indent, skip_attrs, _ui_name))
# end def formatted

def formatted_iter \
        ( obj, AQ = None, level = 1, indent = "  ", skip_attrs = {}
        , _ui_name = None
        ) :
    if AQ is None :
        AQ = Selector.editable
    head = indent * level
    yield _ui_name or obj.ui_name_T
    for ak in AQ (obj) :
        t_skip_attrs = skip_attrs.get (ak.name, {})
        show         = isinstance (t_skip_attrs, dict) or not t_skip_attrs
        if show and ak.has_substance (obj) :
            if ak.E_Type :
                t_skip_attrs = dict \
                    (skip_attrs.get (ak.E_Type.type_name, {}), ** t_skip_attrs)
            fa = formatted_attr (ak, obj, AQ, level+1, indent, t_skip_attrs)
            if fa is not None :
                yield head + fa
# end def formatted_iter

if __name__ != "__main__" :
    MOM._Export ("formatted")
### __END__ MOM.formatted
