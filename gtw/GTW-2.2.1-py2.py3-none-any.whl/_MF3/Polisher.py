# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.MF3.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.MF3.Polisher
#
# Purpose
#    Polishers for MF3 fields
#
# Revision Dates
#    26-Apr-2016 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _MOM                     import MOM
from   _TFL                     import TFL

from   _MOM.import_MOM          import Q

import _MOM._Attr.Polisher

from   _TFL._Meta.M_Class       import BaM
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import uniq
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL._Meta.Property

from   itertools                import chain as ichain

class _MF3_Polisher_ (TFL.Meta.Object) :

    _real_name = "Polisher"

    def __init__ (self, elem) :
        self.elem      = elem
        self.polisher  = elem.attr.polisher
    # end def __init__

    def __call__ (self, * args, ** kw) :
        return self.polisher (* args, ** kw)
    # end def __call__

    @TFL.Meta.Once_Property
    def elems (self) :
        def _gen (self) :
            ep = self.elem.parent
            for n in self.polisher.names :
                elem = ep.get (n)
                if elem is not None :
                    yield elem
        return tuple (_gen (self))
    # end def elems

    @TFL.Meta.Once_Property
    def field_ids (self) :
        return tuple (e.id for e in self.elems)
    # end def field_ids

    @TFL.Meta.Once_Property
    def id (self) :
        elem = self.elem
        return elem._mapped_id (elem.root.buddies_map, self.sig)
    # end def id

    @TFL.Meta.Once_Property
    def sig (self) :
        return tuple (str (id) for id in sorted (self.field_ids))
    # end def sig

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        result = getattr (self.polisher, name)
        setattr (self, name, result)
        return result
    # end def __getattr__

Polisher = _MF3_Polisher_ # end class

if __name__ != "__main__" :
    GTW.MF3._Export ("*")
### __END__ GTW.MF3.Polisher
