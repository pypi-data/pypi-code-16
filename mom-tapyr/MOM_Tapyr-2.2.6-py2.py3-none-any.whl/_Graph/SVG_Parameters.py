# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Graph.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Graph.SVG_Parameters
#
# Purpose
#    Default parameters for MOM.Graph.SVG renderer
#
# Revision Dates
#    29-Aug-2012 (CT) Creation
#    20-Sep-2012 (RS) Add `link_bg`, change `attr_marker_size`
#    20-Sep-2012 (RS) Fix marker parameters for new size computation
#    20-Sep-2012 (RS) smaller `attr_marker_size`
#    25-Sep-2012 (CT) Add `partial_node_opacity`
#    11-Oct-2016 (CT) Use `TFL.Parameters`, not `GTW.Parameters`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM                   import MOM
import _MOM._Graph

from   _TFL.Color             import RGB_X
from   _TFL.Parameters        import Definition, P, P_dict

class SVG_Parameters (Definition) :
    """Default parameters for MOM.Graph.SVG renderer."""

    class color (Definition) :

        attr_link           = RGB_X     ("#FFA022", alpha = 0.70)
        is_a_link           = RGB_X     ("#0088DD", alpha = 0.45)
        link_bg             = RGB_X     ("#FFFFFF")
        node_bg             = RGB_X     ("#EDEDED")
        node_border         = RGB_X     ("#999999")
        role_link           = RGB_X     ("#666666")
        text                = RGB_X     ("#000033")

    # end class color

    attr_marker_ref_x       = None
    attr_marker_size        = 4
    font_family             = "sans-serif"
    font_size               = 18
    font_char_width         = font_size  / 2.0
    is_a_marker_ref_x       = 8
    is_a_marker_size        = 3
    line_height             = font_size  * 1.5
    link_opacity            = 1.0
    link_stroke_width       = 5
    node_border_width       = 4
    node_opacity            = 1.0
    partial_node_opacity    = 0.6

# end class SVG_Parameters

if __name__ != "__main__" :
    MOM.Graph._Export ("SVG_Parameters")
### __END__ MOM.Graph.SVG_Parameters
