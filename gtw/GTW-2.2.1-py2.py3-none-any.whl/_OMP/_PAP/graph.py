# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.graph
#
# Purpose
#    Graph describing PAP (partial) object model
#
# Revision Dates
#    24-Sep-2012 (CT) Creation
#    11-Oct-2012 (CT) Add `Address_Position`, `Url`
#    12-Oct-2012 (CT) Add `Nickname` if provided by `PAP`, i.e., was imported
#     9-Nov-2012 (CT) Add `IM_Handle` if provided by `PAP`, i.e., was imported
#     9-Nov-2012 (CT) Rotate graph by roughly 90 degrees
#     7-May-2013 (CT) Add `Association`, `Person_has_Account`, if imported
#     7-May-2013 (CT) Shift `Subject_has_Property` to center of graph
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#    10-Aug-2015 (CT) Add `Group`, `Legal_Entity`, `Adhoc_Group`,
#                     `Person_in_Group`; shift children of `Property` to `E`
#    15-Sep-2015 (CT) Remove `import_XXX` from `__main__`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                   import GTW
from   _MOM                   import MOM
from   _TFL                   import TFL

import _GTW._OMP._PAP

from   _MOM._Graph.Spec       import Attr, Child, ET, IS_A, Role, Skip

import _MOM._Graph.Command
import _MOM._Graph.Entity

from   _TFL._D2               import Cardinal_Direction as CD
from   _TFL.I18N              import _, _T

import _TFL._Meta.Once_Property

def graph (app_type) :
    """Class/association graph displaying PAP partial object model"""
    ag_p    = hasattr (GTW.OMP.PAP, "Adhoc_Group")
    ass_p   = hasattr (GTW.OMP.PAP, "Association")
    le_p    = hasattr (GTW.OMP.PAP, "Legal_Entity")
    shp_off = CD.S
    result  = MOM.Graph.Spec.Graph \
        ( app_type
        , ET.PAP.Subject_has_Property
            ( Role.left
                ( Child.PAP.Person
                    ( offset      = CD.N
                    )
                , offset = CD.W
                )
            , Role.right
                ( Child.PAP.Address
                    ( ET.PAP.Address_Position
                        ( offset      = CD.S if (ag_p or le_p) else CD.W
                        )
                    , offset      = shp_off + 3 * CD.W
                    )
                , Child.PAP.Email
                    ( offset      = shp_off + 2 * CD.W
                    )
                , Child.PAP.Phone
                    ( offset      = shp_off + 1 * CD.W
                    )
                , Child.PAP.Url
                    ( offset      = shp_off
                    )
                , offset = CD.E
                )
            )
        , desc  = _T
            ("Class/association graph displaying PAP partial object model")
        , title = _T ("PAP graph")
        )
    if hasattr (GTW.OMP.PAP, "Group") :
        g_args = ()
        if hasattr (GTW.OMP.PAP, "Person_in_Group") :
            g_args = \
                ( ET.PAP.Person_in_Group
                    ( Role.left  ()
                    , Role.right ()
                    , offset      = CD.N
                    )
                ,
                )
        result ["PAP.Subject"]._add \
            ( Child.PAP.Group
                ( * g_args
                , offset      = CD.W
                )
            )
        if le_p :
            result ["PAP.Group"]._add \
                ( Child.PAP.Legal_Entity
                    ( offset      = CD.W
                    , source_side = "E"
                    , target_side = "W"
                    )
                )
            if ass_p :
                result ["PAP.Legal_Entity"]._add \
                    ( Child.PAP.Association
                        ( offset      = CD.N
                        )
                    )
            if hasattr (GTW.OMP.PAP, "Company") :
                result ["PAP.Legal_Entity"]._add \
                    ( Child.PAP.Company
                        ( offset      = CD.S
                        )
                    )
        if ag_p :
            result ["PAP.Group"]._add \
                ( Child.PAP.Adhoc_Group
                    ( offset      = CD.W + CD.S *
                        (-1 if not ass_p else (2 if le_p else 0))
                    , source_side = "E"
                    , target_side = "W"
                    )
                )
    if hasattr (GTW.OMP.PAP, "IM_Handle") :
        result ["PAP.Property"]._add \
            ( Child.PAP.IM_Handle
                ( offset      = shp_off + CD.E
                )
            )
    if hasattr (GTW.OMP.PAP, "Nickname") :
        result ["PAP.Property"]._add \
            ( Child.PAP.Nickname
                ( offset      = CD.E
                , source_side = "W"
                , target_side = "E"
                )
            )
    if hasattr (GTW.OMP.PAP, "Person_has_Account") :
        result ["PAP.Person"]._add \
            ( ET.PAP.Person_has_Account
                ( Role.left  (guide_offset = 1.0)
                , Role.right
                    ( offset  = CD.E
                    )
                , offset      = CD.E
                )
            )
    return result
# end def graph

class Command (MOM.Graph.Command) :

    @TFL.Meta.Class_and_Instance_Once_Property
    def PNS (self) :
        return GTW.OMP.PAP
    # end def PNS

    def import_all (self) :
        import _GTW._OMP._Auth
        self.__super.import_all  ()
        GTW.OMP.Auth._Import_All ()
    # end def import_all

# end class Command

if __name__ != "__main__" :
    GTW.OMP.PAP._Export_Module ()
else :
    Command () ()
### __END__ GTW.OMP.PAP.graph
