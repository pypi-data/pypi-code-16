# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.SRM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.SRM.Ranking
#
# Purpose
#    Model a ranking list for sailboat regattas
#
# Revision Dates
#    17-Aug-2014 (CT) Creation
#    30-Mar-2015 (CT) Set `treshold` for `Ranking.name` to `0`;
#                     ditto for `Regatta_in_Ranking.right`
#    25-Feb-2016 (CT) Set `nick.unique_p`, don't define explicit `Pred.Unique`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._SRM.Regatta

from   _TFL.I18N                import _, _T, _Tn
import _TFL.Decorator

_Ancestor_Essence = GTW.OMP.SRM.Object

class Ranking (_Ancestor_Essence) :
    """Ranking list for sailboat regattas"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_String) :
            """Name of the ranking list"""

            kind               = Attr.Primary
            completer          = Attr.Completer_Spec (0, Attr.Selector.primary)
            max_length         = 32

        # end class name

        class nick (A_String) :
            """Nickname of ranking list"""

            kind               = Attr.Required
            max_length         = 8
            unique_p           = True

        # end class nick

    # end class _Attributes

    def points (self, boat_in_regatta) :
        """Ranking list points of `boat_in_regatta`"""
        scope   = self.home_scope
        regatta = boat_in_regatta.regatta
        if regatta.races_counted and regatta.starters_rl :
            rir = scope.SRM.Regatta_in_Ranking.instance (regatta, self)
            if rir is not None :
                result = \
                    ( ( (regatta.starters_rl + 1)
                      - (boat_in_regatta.points / regatta.races_counted)
                      )
                    * (100.0 / regatta.starters_rl)
                    * rir.factor
                    )
                return result
    # end def points

# end class Ranking

_Ancestor_Essence = GTW.OMP.SRM.Link2

class Regatta_in_Ranking (_Ancestor_Essence) :
    """Regatta participating in ranking list"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Regatta that participates in ranking"""

            role_type          = GTW.OMP.SRM.Regatta
            auto_rev_ref       = True
            completer          = Attr.E_Completer_Spec (Attr.Selector.primary)

        # end class left

        class right (_Ancestor.right) :
            """Ranking the regatta participates in"""

            role_type          = Ranking
            auto_rev_ref       = True
            completer          = Attr.E_Completer_Spec (0, Attr.Selector.primary)

        # end class right

        ### Non-primary attributes

        class factor (A_Float) :
            """Weight of this regatta in computation of ranking list points."""

            kind               = Attr.Optional
            raw_default        = "1.0"
            format             = "%6.2f"
            min_value          = 0.40
            max_value          = 2.00

        # end class factor

    # end class _Attributes

# end class Regatta_in_Ranking

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Ranking
