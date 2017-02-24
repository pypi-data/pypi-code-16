# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SWP.graph
#
# Purpose
#    Graph describing SWP (partial) object model
#
# Revision Dates
#    25-Sep-2012 (CT) Creation
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#    15-Sep-2015 (CT) Remove `import_XXX` from `__main__`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                   import GTW
from   _MOM                   import MOM
from   _TFL                   import TFL

import _GTW._OMP._SWP

from   _MOM._Graph.Spec       import Attr, Child, ET, IS_A, Role, Skip

import _MOM._Graph.Command
import _MOM._Graph.Entity

from   _TFL._D2               import Cardinal_Direction as CD
from   _TFL.I18N              import _, _T

import _TFL._Meta.Once_Property

def graph (app_type) :
    """Class/association graph displaying SWP partial object model"""
    return MOM.Graph.Spec.Graph \
        ( app_type
        , ET.SWP.Gallery
            ( IS_A.SWP.Object_PN
                ( Child.SWP.Page
                    ( Child.SWP.Page_Y (offset = CD.W)
                    , Child.SWP.Clip_X (offset = CD.E)
                    , offset = CD.S
                    )
                , ET.SWP.Clip_O  (offset = CD.E)
                , offset = CD.S
                )
            , ET.SWP.Picture (offset = CD.E)
            )
        , desc  = _T
            ("Class/association graph displaying SWP partial object model")
        , title = _T ("SWP graph")
        )
# end def graph

class Command (MOM.Graph.Command) :

    @TFL.Meta.Class_and_Instance_Once_Property
    def PNS (self) :
        return GTW.OMP.SWP
    # end def PNS

# end class Command

if __name__ != "__main__" :
    GTW.OMP.SWP._Export_Module ()
else :
    Command () ()
### __END__ GTW.OMP.SWP.graph
