# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.SWP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.SWP.Random_Picture
#
# Purpose
#    Access to random instances of `GTW.OMP.SWP.Picture` weighted by `prio` of
#    the gallery
#
# Revision Dates
#    14-Dec-2015 (CT) Creation
#    15-Dec-2015 (CT) Add `Random_Picture.Manager` with method `generate`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM.import_MOM          import *
from   _GTW                     import GTW

import _GTW._OMP._SWP.Picture

from   _TFL.I18N                import _, _T, _Tn

import random

_Ancestor_Essence = GTW.OMP.SWP.Link1

class _Random_Picture_Manager_ (_Ancestor_Essence.M_E_Type.Manager) :
    """E-Type manager for `Random_Picture`."""

    def generate (self) :
        """Generate instances of `Random_Picture`."""
        def _gen (scope) :
            for p in scope.SWP.Picture.query \
                    (Q.left.prio > 0, ~ Q.random_pictures) :
                for i in range (p.left.prio) :
                    yield p
        offs = self.count
        pics = list    (_gen (self.home_scope))
        random.shuffle (pics)
        for i, p in enumerate (pics, offs) :
            self (p, i)
    # end def generate

# end class _Random_Picture_Manager_

class Random_Picture (_Ancestor_Essence) :
    """Random picture."""

    Manager               = _Random_Picture_Manager_
    electric              = True
    refuse_links          = set (["EVT.Event"])
    show_in_UI            = False

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Picture selected randomly."""

            role_type          = GTW.OMP.SWP.Picture
            Kind_Mixins        = (MOM.Attr.Just_Once_Mixin, )
            ui_allow_new       = False

        # end class left

        class number (A_Int) :
            """Sequence number of random picture."""

            kind               = Attr.Primary
            Kind_Mixins        = (MOM.Attr.Just_Once_Mixin, )
            min_value          = 0

        # end class number

    # end class _Attributes

# end class Random_Picture

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Random_Picture
