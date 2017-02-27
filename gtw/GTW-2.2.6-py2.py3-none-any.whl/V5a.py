# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.V5a
#
# Purpose
#    Definition of javascript modules provided by V5a
#
# Revision Dates
#    14-Jan-2016 (CT) Creation
#    20-Jan-2016 (CT) ...Creation
#    21-Jan-2016 (CT) Add `V5a_gallery`
#    23-Jan-2016 (CT) Add `V5a_wrapped`...
#    26-Jan-2016 (CT) Add `V5a_ajax`...
#     5-May-2016 (CT) Add `V5a_new_window`
#    10-Jun-2016 (CT) Add `V5a_form_field`
#    11-Oct-2016 (CT) Use `CHJ.Media`, not `GTW.Media`
#    19-Jan-2017 (CT) Add `V5a_is_in_viewport`
#                     + Adapt `requires` of `V5a_nav_off_canvas`
#    21-Jan-2017 (CT) Change `requires` of `V5a_nav_off_canvas`, again
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CHJ        import CHJ
from   _GTW        import GTW
import _CHJ.Media

### infrastructure
CHJ.Script \
    ( src       = "/media/GTW/js/V5a/V5a.js"
    , name      = "V5a"
    , rank      = -70  ## should be loaded first
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/event_map.js"
    , name      = "V5a_event_map"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/bind.js"
    , name      = "V5a_bind"
    , requires  = (CHJ.Script._.V5a_event_map, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/error.js"
    , name      = "V5a_error"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/ajax.js"
    , name      = "V5a_ajax"
    , requires  =
        ( CHJ.Script._.V5a_bind
        , CHJ.Script._.V5a_error
        , ### if a client of V5a_ajax wants to use
          ### "application/x-www-form-urlencoded", it needs to require
          ### CHJ.Script._.V5a_form_urlencoded
        )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/extend.js"
    , name      = "V5a_extend"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/form_field.js"
    , name      = "V5a_form_field"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/form_urlencoded.js"
    , name      = "V5a_form_urlencoded"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/has_class_all.js"
    , name      = "V5a_has_class_all"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/has_class_any.js"
    , name      = "V5a_has_class_any"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/history_test.js"
    , name      = "V5a_history_test"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/history_push.js"
    , name      = "V5a_history_push"
    , requires  = (CHJ.Script._.V5a_history_test, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/is_in_viewport.js"
    , name      = "V5a_is_in_viewport"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/matches.js"
    , name      = "V5a_matches"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/closest.js"
    , name      = "V5a_closest"
    , requires  = (CHJ.Script._.V5a_matches, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/merge.js"
    , name      = "V5a_merge"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/new_window.js"
    , name      = "V5a_new_window"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/parse_html.js"
    , name      = "V5a_parse_html"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/query.js"
    , name      = "V5a_query"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/scroll_to.js"
    , name      = "V5a_scroll_to"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/select.js"
    , name      = "V5a_select"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/siblings.js"
    , name      = "V5a_siblings"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/string_to_int_array.js"
    , name      = "V5a_string_to_int_array"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/trigger.js"
    , name      = "V5a_trigger"
    , requires  = (CHJ.Script._.V5a_merge, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/type_name.js"
    , name      = "V5a_type_name"
    , requires  = (CHJ.Script._.V5a, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped.js"
    , name      = "V5a_wrapped"
    , requires  = (CHJ.Script._.V5a_select, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_add_class.js"
    , name      = "V5a_wrapped_add_class"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_attr.js"
    , name      = "V5a_wrapped_attr"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_bind.js"
    , name      = "V5a_wrapped_bind"
    , requires  =
        ( CHJ.Script._.V5a_bind
        , CHJ.Script._.V5a_wrapped
        )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_reduce.js"
    , name      = "V5a_wrapped_reduce"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_closest.js"
    , name      = "V5a_wrapped_closest"
    , requires  =
        ( CHJ.Script._.V5a_closest
        , CHJ.Script._.V5a_wrapped_reduce
        )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_filter.js"
    , name      = "V5a_wrapped_filter"
    , requires  = (CHJ.Script._.V5a_wrapped, CHJ.Script._.V5a_matches)
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_has_class.js"
    , name      = "V5a_wrapped_has_class"
    , requires  = (CHJ.Script._.V5a_wrapped_filter, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_children.js"
    , name      = "V5a_wrapped_children"
    , requires  =
        ( CHJ.Script._.V5a_wrapped_filter
        , CHJ.Script._.V5a_wrapped_reduce
        )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_find.js"
    , name      = "V5a_wrapped_find"
    , requires  = (CHJ.Script._.V5a_wrapped_reduce, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_insert_html.js"
    , name      = "V5a_wrapped_insert_html"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_parent.js"
    , name      = "V5a_wrapped_parent"
    , requires  =
        ( CHJ.Script._.V5a_wrapped_filter
        , CHJ.Script._.V5a_wrapped_reduce
        )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_prop.js"
    , name      = "V5a_wrapped_prop"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_remove.js"
    , name      = "V5a_wrapped_remove"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_remove_class.js"
    , name      = "V5a_wrapped_remove_class"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_siblings.js"
    , name      = "V5a_wrapped_siblings"
    , requires  =
        ( CHJ.Script._.V5a_siblings
        , CHJ.Script._.V5a_wrapped_filter
        , CHJ.Script._.V5a_wrapped_reduce
        )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_style.js"
    , name      = "V5a_wrapped_style"
    , requires  =
        ( CHJ.Script._.V5a_merge
        , CHJ.Script._.V5a_wrapped
        )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_toggle_class.js"
    , name      = "V5a_wrapped_toggle_class"
    , requires  = (CHJ.Script._.V5a_wrapped, )
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/wrapped_trigger.js"
    , name      = "V5a_wrapped_trigger"
    , requires  =
        ( CHJ.Script._.V5a_trigger
        , CHJ.Script._.V5a_wrapped
        )
    )

### scripts

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/de_obfuscate_a_nospam.js"
    , name      = "V5a_de_obfuscate_a_nospam"
    , requires  =
        ( CHJ.Script._.V5a_merge
        , CHJ.Script._.V5a_query
        , CHJ.Script._.V5a_string_to_int_array
        )
    )

CHJ.JS_On_Ready \
    ( """$V5a.de_obfuscate_a_nospam ();"""
    , name      = "V5a_de_obfuscate_a_nospam"
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/externalize.js"
    , name      = "V5a_externalize"
    , requires  =
        ( CHJ.Script._.V5a_merge
        , CHJ.Script._.V5a_new_window
        , CHJ.Script._.V5a_wrapped_add_class
        , CHJ.Script._.V5a_wrapped_has_class
        , CHJ.Script._.V5a_wrapped_bind
        )
    )

CHJ.JS_On_Ready \
    ( """$V5a.externalize ();"""
    , name      = "V5a_externalize"
    )

CHJ.JS_On_Ready \
    ( """$V5a.externalize """
      """( { selectors : {external : "form a"}"""
        """, skip_classes : ["button", "internal", "pure-button", "ui-icon"]"""
        """}"""
      """);"""
    , name      = "V5a_Form_externalize"
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/gallery.js"
    , name      = "V5a_gallery"
    , requires  =
        ( CHJ.Script._.V5a_merge
        , CHJ.Script._.V5a_query
        , CHJ.Script._.V5a_scroll_to
        , CHJ.Script._.V5a_wrapped_bind
        )
    )

CHJ.JS_On_Ready \
    ( """$V5a.gallery ();"""
    , name      = "V5a_gallery"
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/nav_off_canvas.js"
    , name      = "V5a_nav_off_canvas"
    , requires  =
        ( CHJ.Script._.V5a_is_in_viewport
        , CHJ.Script._.V5a_merge
        , CHJ.Script._.V5a_query
        , CHJ.Script._.V5a_scroll_to
        , CHJ.Script._.V5a_wrapped_bind
        )
    )
CHJ.JS_On_Ready \
    ( """$V5a.nav_off_canvas ();"""
    , name      = "V5a_nav_off_canvas"
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/page_notifications.js"
    , name      = "V5a_page_notifications"
    , requires  =
        ( CHJ.Script._.V5a_merge
        , CHJ.Script._.V5a_query
        , CHJ.Script._.V5a_wrapped_bind
        )
    )
CHJ.JS_On_Ready \
    ( """$V5a.page_notifications ();"""
    , name      = "V5a_page_notifications"
    )

CHJ.Script \
    ( src       = "/media/GTW/js/V5a/pixpander.js"
    , name      = "V5a_pixpander"
    , requires  =
        ( CHJ.Script._.V5a_bind
        , CHJ.Script._.V5a_merge
        , CHJ.Script._.V5a_query
        )
    )
CHJ.JS_On_Ready \
    ( """$V5a.pixpander ();"""
    , name      = "V5a_pixpander"
    )

### __END__ GTW.V5a
