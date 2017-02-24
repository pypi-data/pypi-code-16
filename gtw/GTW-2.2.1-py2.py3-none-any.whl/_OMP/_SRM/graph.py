# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SRM.graph
#
# Purpose
#    Graph describing SRM (partial) object model
#
# Revision Dates
#    17-Aug-2012 (CT) Creation
#    21-Aug-2012 (CT) Add `Team_has_Boat_in_Regatta`, `Race_Result`
#    31-Aug-2012 (CT) Adapt to MOM.Graph.Spec API change
#     3-Sep-2012 (CT) Add `Page`, specify `source_side` for `Crew_Member`
#    24-Sep-2012 (CT) Add `Command`, rename from `Graph.py` to `graph.py`
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#    15-Sep-2015 (CT) Remove `import_XXX` from `__main__`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                   import GTW
from   _MOM                   import MOM
from   _TFL                   import TFL

import _GTW._OMP._SRM

from   _MOM._Graph.Spec       import Attr, Child, ET, IS_A, Role, Skip

import _MOM._Graph.Command
import _MOM._Graph.Entity

from   _TFL._D2               import Cardinal_Direction as CD
from   _TFL.I18N              import _, _T

import _TFL._Meta.Once_Property

def graph (app_type) :
    """Class/association graph displaying SRM partial object model"""
    return MOM.Graph.Spec.Graph \
        ( app_type
        , ET.SRM.Boat_in_Regatta
            ( Role.left
                ( Role.left (offset = CD.W)
                , offset = CD.W
                )
            , Role.right
                ( Role.left
                    ( Attr.club (offset = CD.N * 2)
                    , ET.SRM.Page
                        ( Attr.event
                        , offset = CD.S
                        )
                    , offset = CD.E
                    )
                , offset = CD.E
                )
            , ET.SRM.Crew_Member
                ( Role.left  (anchor = False, source_side = "W")
                , Role.right (anchor = False, source_side = "W")
                , offset = CD.NE
                )
            , ET.SRM.Team_has_Boat_in_Regatta
                ( Role.left
                    ( ET.SRM.Regatta_C
                        ( IS_A.SRM.Regatta
                        , offset = CD.E
                        )
                    , offset = CD.S
                    )
                , offset = CD.S
                )
            , ET.SRM.Race_Result (offset = CD.SW)
            , Attr.skipper
                ( Role.left
                    ( IS_A.PAP.Subject (offset = CD.E * 2)
                    , offset = CD.N
                    )
                , Attr.club (IS_A.PAP.Subject)
                , offset = CD.N * 2
                )
            )
        , desc  = _T
            ("Class/association graph displaying SRM partial object model")
        , title = _T ("SRM graph")
        )
# end def graph

class Command (MOM.Graph.Command) :

    @TFL.Meta.Class_and_Instance_Once_Property
    def PNS (self) :
        return GTW.OMP.SRM
    # end def PNS

    def import_all (self) :
        import _GTW._OMP._PAP
        GTW.OMP.PAP._Import_All ()
        self.__super.import_all ()
    # end def import_all

# end class Command

if __name__ != "__main__" :
    GTW.OMP.SRM._Export_Module ()
else :
    Command () ()
### __END__ GTW.OMP.SRM.graph
