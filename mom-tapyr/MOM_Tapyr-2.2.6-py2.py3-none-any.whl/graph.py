# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
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
#    MOM.graph
#
# Purpose
#    Graph describing MOM meta object model
#
# Revision Dates
#    14-Sep-2015 (CT) Creation
#    15-Sep-2015 (CT) Add `desc` and `title` to `Graph` spec
#    15-Sep-2015 (CT) Remove imports from `__main__`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                   import MOM
from   _TFL                   import TFL

from   _MOM._Graph.Spec       import Attr, Child, ET, IS_A, Role, Skip

import _MOM._Graph.Command
import _MOM._Graph.Entity

from   _TFL._D2               import Cardinal_Direction as CD
from   _TFL.I18N              import _, _T

import _TFL._Meta.Once_Property

def graph (app_type) :
    """Class/association graph describing MOM meta object model"""
    doc_p = hasattr (MOM, "Document")
    iht_p = hasattr (MOM, "Id_Entity_has_Tag")
    result = MOM.Graph.Spec.Graph \
        ( app_type
        , ET.MOM.Id_Entity
            ( Child.MOM.Object    (offset     = CD.N)
            , Child.MOM.Link1
                ( Attr.left       (guide_prio = 0.25)
                , offset     = CD.W
                )
            , Child.MOM._Link_n_
                ( Attr.left       (guide_prio = 0.25)
                , Attr.right      (guide_prio = 0.75)
                , Child.MOM.Link2
                    ( offset = CD.E
                    )
                , Child.MOM.Link3
                    ( Attr.middle ()
                    , offset = CD.W
                    )
                , guide_prio = 0.5
                , offset     = CD.S
                )
            ,
            )
        , desc  = _T ("Graph displaying MOM meta object model")
        , title = _T ("MOM graph")
        )
    if doc_p :
        result ["MOM.Link1"]._add \
            ( Child.MOM.Document
                ( offset     = CD.N
                )
            )
    if iht_p :
        result ["MOM.Id_Entity"]._add \
            ( ET.MOM.Id_Entity_has_Tag
                ( IS_A.MOM.Link2
                , Role.left  ()
                , Role.right
                    ( IS_A.MOM.Object
                    , offset     = CD.N
                    )
                , offset     = CD.E
                )
            )
    return result
# end def graph

class Command (MOM.Graph.Command) :

    @TFL.Meta.Class_and_Instance_Once_Property
    def PNS (self) :
        return MOM
    # end def PNS

# end class Command

if __name__ != "__main__" :
    MOM._Export_Module ()
else :
    Command () ()
### __END__ MOM.graph
