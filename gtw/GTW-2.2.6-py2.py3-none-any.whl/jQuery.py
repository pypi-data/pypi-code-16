# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    jQuery
#
# Purpose
#    Definition of the javascript and CSS file if jQuery and jQuery UI should
#    be used.
#
# Revision Dates
#     1-May-2010 (MG) Creation
#     3-Aug-2010 (CT) `de_obfuscate_a` added
#     4-Aug-2010 (CT) `fix_a_nospam` factored
#     7-Oct-2010 (CT) `GTW_Gallery` added
#    10-Oct-2010 (CT) `GTW_Externalize` added
#    18-Oct-2010 (CT) `GTW_pixpander` added
#    15-Nov-2010 (CT) `GTW_week_roller` added
#    19-Nov-2010 (CT) `Modernizr` added
#    12-Jan-2011 (CT) `GTW_Input` and `GTW_Label` added
#    20-Jan-2011 (CT) Functions `GTW_Gallery`, `GTW_Externalize`,
#                     `GTW_pixpander`, `GTW_week_roller` renamed to lowercase
#    26-Jan-2011 (CT) `GTW.js` added
#     1-Feb-2011 (CT) Changed `src` of GTW-specific js-files
#     7-Apr-2011 (MG) Use jQuery 1.5.2
#     7-Apr-2011 (MG) Definitions for `jqPlot` added
#     1-Jun-2011 (CT) `GTW_postify_a` added
#    13-Sep-2011 (MG) `s/sort_key/rank/g`
#    19-Oct-2011 (CT) Use jQuery 1.6.4 (but without version number in filename)
#     8-Nov-2011 (CT) Add `GTW_jq_util`
#    22-Nov-2011 (CT) Add `GTW_query_restriction`
#    26-Nov-2011 (CT) Add `GTW_e_type_admin`, `GTW_buttonify`
#     2-Dec-2011 (CT) Use `modernizr.custom.js` instead of specific version
#     6-Dec-2011 (CT) Add `GTW_jsonify`, `GTW_afs_elements`, `GTW_inspect`,
#                     `GTW_jq_afs`, and `GTW_autocomplete`
#    15-Dec-2011 (CT) Add `GTW_UI_Icon_Map`, `GTW_e_type_selector`
#     3-Jan-2012 (CT) Add `requires` to `Script` definitions
#    21-Feb-2012 (CT) Add `GTW_L`
#    29-Feb-2012 (CT) Add more `requires` to `GTW_jq_af`
#     7-Mar-2012 (CT) Add `GTW_e_type_selector` to `GTW_jq_afs`
#    17-Aug-2012 (MG) Remove `jqPlot`
#    25-Sep-2012 (CT) Add `GTW_pns_doc_graph`
#     4-Dec-2012 (CT) Add `//` to `JS_On_Ready` of `GTW_Externalize`
#    29-Apr-2013 (CT) Move `gtw_externalize` and `fix_a_nospam` to `GTW_jq_util`
#     1-May-2013 (CT) Add `GTW_hd_input`
#    17-Jan-2014 (CT) Add `GTW_Form_Externalize`
#    20-Jan-2014 (CT) Fix `GTW_Form_Externalize` to not break buttons
#    20-Feb-2014 (CT) Add `GTW_nav_off_canvas`
#    29-Apr-2014 (CT) Add `GTW_jq_mf3`
#     3-May-2014 (CT) Add `leaflet`
#     8-Jul-2014 (CT) Add `a.pure-button` to `.not` clause of
#                     `GTW_Form_Externalize`
#    29-Aug-2014 (CT) Remove `AFS` specific definitions
#    24-Oct-2014 (CT) Add `GTW_button_pure`
#    30-Oct-2014 (CT) Add dependencies to `GTW_button_pure`
#    31-Oct-2014 (CT) Fix typo that fails in jQuery 1.11.1
#    10-Dec-2014 (CT) Remove dependencies to `GTW_buttonify`
#    12-May-2015 (CT) Add missing dependency `GTW_L` to `query_restriction`
#     2-Jun-2015 (CT) Remove `GTW_postify_a`
#     9-Jun-2015 (CT) Add `.not ("a.internal")` to `GTW_Externalize`
#    15-Dec-2015 (CT) Remove obsolete definitions
#                     (GTW_buttonify, GTW_Input, GTW_Label)
#    20-Jan-2016 (CT) Remove GTW_Externalize, de_obfuscate_a,
#                     GTW_nav_off_canvas, GTW_pixpander
#    20-Jan-2016 (CT) Add `V5a_history_push`
#    21-Jan-2016 (CT) Remove GTW_Gallery
#    22-Jan-2016 (CT) Remove jQuery_Gritter, GTW_UI_Icon_Map, GTW_jsonify
#     5-May-2016 (CT) Add `V5a_new_window` to `requires` of `pns_doc_graph`
#    10-Jun-2016 (CT) Add `V5a_form_field` to `requires` of `e_type_selector`
#    11-Oct-2016 (CT) Use `CHJ.Media`, not `GTW.Media`
#    ««revision-date»»···
#--

from   _CHJ        import CHJ
from   _GTW        import GTW
import _CHJ.Media
import _GTW.V5a

CHJ.Script \
    ( src       = "/media/GTW/js/modernizr.custom.js"
    , may_cache = False
    , name      = "Modernizr"
    , rank      = -10000   ## should be loaded really first
    )

if __debug__ :
    CHJ.Script \
        ( src       = "/media/GTW/js/jquery.js"
        , rank      = -101  ## should be loaded first
        , name      = "jQuery"
        )
    CHJ.Script \
        ( src       = "/media/GTW/js/jquery-ui.js"
        , name      = "jQuery_UI"
        , rank      = -100  ## should be loaded first
        , requires  = (CHJ.Script._.jQuery, )
        )
else :
    CHJ.Script \
        ( src       = "/media/GTW/js/jquery.min.js"
        , rank      = -101  ## should be loaded first
        , name      = "jQuery"
        )
    CHJ.Script \
        ( src       = "/media/GTW/js/jquery-ui.min.js"
        , name      = "jQuery_UI"
        , rank      = -100  ## should be loaded first
        , requires  = (CHJ.Script._.jQuery, )
        )

CHJ.CSS_Link ("/media/GTW/css/jquery-ui.css", name = "jQuery_UI")

CHJ.Script \
    ( src      = "/media/GTW/js/leaflet.min.js"
    , name     = "leaflet"
    , rank     = -90
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW.js"
    , name     = "GTW"
    , rank     = -50
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/inspect.js"
    , name     = "GTW_inspect"
    , requires = (CHJ.Script._.GTW, )
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/L.js"
    , name     = "GTW_L"
    , requires = (CHJ.Script._.GTW, )
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/util.js"
    , name     = "GTW_util"
    , requires =
        ( CHJ.Script._.GTW
        , CHJ.Script._.V5a_history_push
        )
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/util.js"
    , name     = "GTW_jq_util"
    , requires =
        ( CHJ.Script._.GTW_util
        , CHJ.Script._.jQuery
        )
    )
CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/autocomplete.js"
    , name     = "GTW_autocomplete"
    , requires = (CHJ.Script._.jQuery_UI, CHJ.Script._.GTW_jq_util)
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/button_pure.js"
    , name     = "GTW_button_pure"
    , rank     = -10
    , requires = (CHJ.Script._.jQuery_UI, CHJ.Script._.GTW)
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/hd_input.js"
    , name     = "GTW_hd_input"
    , requires = (CHJ.Script._.jQuery, )
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/pns_doc_graph.js"
    , name     = "GTW_pns_doc_graph"
    , requires = (CHJ.Script._.jQuery, CHJ.Script._.V5a_new_window)
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/e_type_selector.js"
    , name     = "GTW_e_type_selector"
    , requires =
        ( CHJ.Script._.GTW_autocomplete
        , CHJ.Script._.GTW_button_pure
        , CHJ.Script._.GTW_jq_util
        , CHJ.Script._.GTW_util
        , CHJ.Script._.V5a_form_field
        )
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/query_restriction.js"
    , name     = "GTW_query_restriction"
    , requires =
        ( CHJ.Script._.GTW_autocomplete
        , CHJ.Script._.GTW_button_pure
        , CHJ.Script._.GTW_e_type_selector
        , CHJ.Script._.GTW_jq_util
        , CHJ.Script._.GTW_util
        , CHJ.Script._.GTW_L
        , CHJ.Script._.V5a_history_push
        )
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/e_type_admin.js"
    , name     = "GTW_e_type_admin"
    , requires =
        ( CHJ.Script._.jQuery_UI
        , CHJ.Script._.GTW_query_restriction
        )
    )
CHJ.JS_On_Ready \
    ( """$GTW.ETA$.setup_obj_list (); """
    , name = "GTW_e_type_admin"
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/mf3.js"
    , name     = "GTW_jq_mf3"
    , requires =
        ( CHJ.Script._.GTW_autocomplete
        , CHJ.Script._.GTW_e_type_selector
        , CHJ.Script._.GTW_util
        , CHJ.Script._.GTW_L
        )
    )

CHJ.Script \
    ( src      = "/media/GTW/js/GTW/jQ/week_roller.js"
    , name = "GTW_week_roller"
    , requires =
        ( CHJ.Script._.jQuery_UI
        , CHJ.Script._.GTW_util
        , CHJ.Script._.V5a_history_push
        )
    )
CHJ.JS_On_Ready \
    ( """$(".week-roller").gtw_week_roller (); """
    , name = "GTW_week_roller"
    )

if __name__ != "__main__" :
    GTW._Export ("*")
### __END__ GTW.jQuery
