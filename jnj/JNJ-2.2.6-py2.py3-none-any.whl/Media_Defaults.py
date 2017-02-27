# -*- coding: utf-8 -*-
# Copyright (C) 2011-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package JNJ.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    JNJ.Media_Defaults
#
# Purpose
#    Provide defaults for media fragments in html/*.media
#
# Revision Dates
#     1-Jan-2011 (CT) Creation
#     2-Jan-2011 (CT) Creation continued
#     4-Jan-2011 (CT) Creation continued..
#    14-Jan-2011 (CT) Use `GTW.Parameters.Definition` to allow lazy
#                     references with `P` and `P_dict`
#    22-Mar-2011 (CT) `afs`
#    22-Mar-2011 (CT) `afs` continued
#    29-Mar-2011 (CT) `afs` continued..
#    30-Mar-2011 (CT) `afs` continued...
#    19-May-2011 (CT) `afs` continued....
#    16-Oct-2011 (MG) `Debugger` added
#    24-Oct-2011 (CT) `color_spec_heading_rev` added
#    24-Oct-2011 (CT) `tablesorter` added
#    24-Nov-2011 (CT) Add `color_spec_selected_rev`
#    23-Feb-2012 (CT) Add `color_status_{bad,good,missing}`, `afs.status_size`
#    23-Feb-2012 (CT) Add `color_bg_bad` and `color_bg_missing`
#     1-Mar-2012 (CT) Change `pg_main_max_width` from `Em (50)` to `Em (45)`
#     8-Mar-2012 (CT) Add `color_bg_menu`
#    10-Aug-2012 (CT) Add `color_spec_sub_heading`, `color_spec_term`
#     7-Mar-2013 (CT) Add `border_added` and `border_deleted`
#     3-Apr-2013 (CT) Add `Rule`, `Rule.clearfix`
#     8-Apr-2013 (CT) Add lots of rules to `Rule`, e.g., `disabled`, `focus`...
#     7-Jan-2014 (CT) Add some more muted colors
#    21-Jan-2014 (CT) Add `breakpoint`
#    20-Feb-2014 (CT) Add `Rule.pg_nav_show`, `.pg_nav_show_a`
#    20-Feb-2014 (CT) Add `breakpoint.broad` and `.very_narrow`
#     8-Apr-2014 (CT) Improve `clearfix`
#    12-Apr-2014 (CT) Use `Border.P`, not `P_Border`
#    15-May-2014 (CT) Add `color_lightest_grey`
#    15-May-2014 (CT) Add `breakpoint.quite_narrow`
#     9-Jul-2014 (CT) Add `Rule.rotate_45_left`
#    26-Aug-2014 (CT) Add `pure` parameters
#     3-Sep-2014 (CT) Add `Rule.hidden`
#     3-Dec-2014 (CT) Add `color.alphabet_max_contrast_colors` and
#                     `color.kellys_max_contrast_colors`
#    16-Jan-2015 (CT) Change `nav_col.width` and `col_padding` to unit `Rem`
#    23-Jan-2015 (CT) Add `color_jnd_grey`, reduce contrast of `color_spec_row1`
#    23-Jan-2015 (CT) Factor `line_height*` parameters
#    15-Feb-2015 (CT) Add `menu_icon`
#    24-Mar-2015 (CT) Add `Rule.input_focus`
#     8-Apr-2015 (CT) Change `font_family_print` to "serif" to void font
#                     substitution by the printer
#     2-Dec-2015 (CT) Fix `Rule.visited`
#     2-Dec-2015 (CT) Change `nav_col.color_spec_link_current.background_color`
#    31-Dec-2015 (CT) Change `pg_nav_show` to allow embedded rel-nav buttons
#    11-Oct-2016 (CT) Import from `CHJ`, not `GTW`
#    27-Dec-2016 (CT) Add `breakpoint.really_narrow`
#    12-Jan-2017 (CT) Add `breakpoint.supports_two_column`
#    13-Jan-2017 (CT) Add `body_margin`, `hidden_collapse`, `target_visible`,
#                     `visible`
#    16-Jan-2017 (CT) Add `border_double`, `border_simple_light`
#    16-Jan-2017 (CT) Change `nav_col` to `nav.main`; modernize nav styling
#    16-Jan-2017 (CT) Add `nav.header`, `nav.rel`
#    19-Jan-2017 (CT) Add `Rule.main_nav_off`, `.main_nav_on`
#    ««revision-date»»···
#--

from _CHJ._CSS.import_CSS import *
from _CHJ.Parameters      import \
    ( Definition, P, P_dict, Rule_Definition
    , Rule, Rule_Attr, Rule_Child, Rule_Class, Rule_Pseudo, Rule_Sibling
    )

Color.formatter = RGB_X

class Media_Defaults (Definition) :
    """Provide defaults for CSS fragments in html/*.css"""

    class color (Definition) :

        ### color alphabet
        ### http://eleanormaclure.files.wordpress.com/2011/03/colour-coding.pdf
        ###
        ### The RGB color values were taken with gcolor2's color picker from
        ### colour-coding.pdf
        abc_a                  = RGB_X     ("#C5A1CA")
        abc_b                  = RGB_X     ("#486EB5")
        abc_c                  = RGB_X     ("#82411D")
        abc_d                  = RGB_X     ("#401A57")
        abc_e                  = RGB_X     ("#1F1E1E")
        abc_f                  = RGB_X     ("#335A36")
        abc_g                  = RGB_X     ("#78C259")
        abc_h                  = RGB_X     ("#EDC99A")
        abc_i                  = RGB_X     ("#7F8080")
        abc_j                  = RGB_X     ("#BEDEAE")
        abc_k                  = RGB_X     ("#877A2F")
        abc_l                  = RGB_X     ("#A5C43A")
        abc_m                  = RGB_X     ("#9B247F")
        abc_n                  = RGB_X     ("#253777")
        abc_o                  = RGB_X     ("#E1A131")
        abc_p                  = RGB_X     ("#E6A4B5")
        abc_q                  = RGB_X     ("#50662E")
        abc_r                  = RGB_X     ("#CF2128")
        abc_s                  = RGB_X     ("#A4DBDF")
        abc_t                  = RGB_X     ("#56968C")
        abc_u                  = RGB_X     ("#E0E77B")
        abc_v                  = RGB_X     ("#584EA0")
        abc_w                  = RGB_X     ("#7D1416")
        abc_x                  = RGB_X     ("#F3F190")
        abc_y                  = RGB_X     ("#ECDA43")
        abc_z                  = RGB_X     ("#D55428")

        ### muted colors
        m_aqua                 = RGB_X     ("#7FDBFF")
        m_black                = RGB_X     ("#111111")
        m_blue                 = RGB_X     ("#0088DD")
        m_grey                 = RGB_X     ("#AAAAAA")
        m_fuchsia              = RGB_X     ("#F012BE")
        m_green                = RGB_X     ("#00AA00")
        m_lime                 = RGB_X     ("#01FF70")
        m_maroon               = RGB_X     ("#85144B")
        m_navy                 = RGB_X     ("#001F3F")
        m_red                  = RGB_X     ("#CC3333")
        m_olive                = RGB_X     ("#3D9970")
        m_orange               = RGB_X     ("#FFA022")
        m_pink                 = RGB_X     ("#DD4499")
        m_purple               = RGB_X     ("#AA33BB")
        m_silver               = RGB_X     ("#DDDDDD")
        m_teal                 = RGB_X     ("#33CCCC")
        m_white                = RGB_X     ("#EEEEEE")
        m_yellow               = RGB_X     ("#FFF00F")

        ### pure colors
        p_black                = SVG_Color ("black")
        p_blue                 = SVG_Color ("blue")
        p_cyan                 = SVG_Color ("cyan")
        p_gray = p_grey        = SVG_Color ("gray")
        p_green                = SVG_Color ("green")
        p_lime                 = SVG_Color ("lime")
        p_magenta              = SVG_Color ("magenta")
        p_maroon               = SVG_Color ("maroon")
        p_navy                 = SVG_Color ("navy")
        p_olive                = SVG_Color ("olive")
        p_purple               = SVG_Color ("purple")
        p_red                  = SVG_Color ("red")
        p_teal                 = SVG_Color ("teal")
        p_white                = SVG_Color ("white")
        p_yellow               = SVG_Color ("yellow")

        ### Kelly's 22 colors of maximum contrast
        ### http://www.iscc.org/pdf/PC54_1724_001.pdf
        ### http://burgess-studio.co.uk/colour/
        ### http://eleanormaclure.files.wordpress.com/2011/03/colour-coding.pdf
        ###
        ### The order of colors in Kelly's list was planned so that there
        ### would be maximum contrast between colors in a set if the required
        ### number of colors were always selected in order from the top. So a
        ### set of five colors should be white, black, yellow, purple, and
        ### orange. And if seven colors were required, light blue and red
        ### should be added. Kelly took care of the needs of people with
        ### defective color vision. The first nine colors would be maximally
        ### different for such people as well as for people with normal
        ### vision. These nine colors are also readily distinguishable by
        ### color name.
        ###
        ### The RGB color values were taken with gcolor2's color picker from
        ### colour-coding.pdf
        k_white                = RGB_X     ("#FFFFFF") #  1
        k_black                = RGB_X     ("#1F1E1E") #  2
        k_yellow               = RGB_X     ("#EBCD3F") #  3
        k_purple               = RGB_X     ("#6F308B") #  4
        k_orange               = RGB_X     ("#DB6A28") #  5
        k_light_blue           = RGB_X     ("#98CEE6") #  6
        k_red                  = RGB_X     ("#B91F36") #  7
        k_buff                 = RGB_X     ("#C1BC82") #  8
        k_gray = k_grey        = RGB_X     ("#7F8080") #  9 ———————————
        k_green                = RGB_X     ("#62A647") # 10
        k_purplish_pink        = RGB_X     ("#D386B1") # 11
        k_blue                 = RGB_X     ("#4578B4") # 12
        k_yellowish_pink       = RGB_X     ("#DD8565") # 13
        k_violet               = RGB_X     ("#493896") # 14
        k_orange_yellow        = RGB_X     ("#E1A131") # 15
        k_purplish_red         = RGB_X     ("#91278B") # 16
        k_greenish_yellow      = RGB_X     ("#E9E857") # 17
        k_reddish_brown        = RGB_X     ("#7D1716") # 18
        k_yellow_green         = RGB_X     ("#93AD3C") # 19
        k_yellowish_brown      = RGB_X     ("#6E3515") # 20
        k_reddish_orange       = RGB_X     ("#D12D27") # 21
        k_olive_green          = RGB_X     ("#2C3617") # 22

        kellys_max_contrast_colors = \
          [ k_white
          , k_black
          , k_yellow
          , k_purple
          , k_orange
          , k_light_blue
          , k_red
          , k_buff
          , k_gray
          , k_green
          , k_purplish_pink
          , k_blue
          , k_yellowish_pink
          , k_violet
          , k_orange_yellow
          , k_purplish_red
          , k_greenish_yellow
          , k_reddish_brown
          , k_yellow_green
          , k_yellowish_brown
          , k_reddish_orange
          , k_olive_green
          ]

        ### The order in the following list tries to maximize contrast,
        ### analogously to Kelly's list
        alphabet_max_contrast_colors = \
          [ abc_e
          , abc_y
          , abc_d
          , abc_z
          , abc_s
          , abc_r
          , abc_x
          , abc_i
          , abc_g
          , abc_p
          , abc_b
          , abc_h
          , abc_v
          , abc_o
          , abc_m
          , abc_u
          , abc_w
          , abc_l
          , abc_c
          , abc_a
          , abc_q
          , abc_j
          , abc_n
          , abc_k
          , abc_f
          , abc_t
          ]

    # end class color

    color_bg_bad           = RGB_X     ("#FFEEEE")
    color_bg_menu          = RGB_X     ("#DDEEFF")
    color_bg_missing       = RGB_X     ("#FFFFBB")
    color_desc             = RGB_X     ("#666666")
    color_focus            = SVG_Color ("yellow")
    color_heading          = RGB_X     ("#34444D")
    color_heading_closed   = RGB_X     ("#56666E")
    color_heading_sub      = RGB_X     ("#78888F")
    color_jnd_grey         = RGB_X     ("#F8F8F8")
    color_lightest_grey    = RGB_X     ("#F6F6F6")
    color_lighter_grey     = RGB_X     ("#EDEDED")
    color_light_grey       = RGB_X     ("#DEDEDE")
    color_border_grey      = RGB_X     ("#CCCCCC")
    color_medium_grey      = RGB_X     ("#BEBEBE")
    color_half_grey        = RGB_X     ("#888888")
    color_dark_grey        = RGB_X     ("#444444")
    color_darker_grey      = RGB_X     ("#222222")
    color_selected         = RGB_X     ("#FF6633")
    color_status_bad       = RGB_X     ("#FF6666")
    color_status_good      = RGB_X     ("#AAEEAA")
    color_status_missing   = RGB_X     ("#FFDD00")
    color_target           = RGB_X     ("#FF6633")

    css_arrow_color        = SVG_Color ("red")
    css_arrow_width        = Em (1./2)

    block_margin_bottom    = Em (1./2)

    body_margin            = TRBL (Em (0.2), Em (0.5))

    border_added           = "1px solid "  + P.color.m_red
    border_button          = "2px outset " + P.color_medium_grey
    border_deleted         = "1px solid "  + P.color.m_blue
    border_double          = "2px solid "  + P.color_medium_grey
    border_double_light    = "2px solid "  + P.color_light_grey
    border_selected        = "2px solid "  + P.color_selected
    border_simple          = "1px solid "  + P.color_medium_grey
    border_simple_light    = "1px solid "  + P.color_light_grey

    button_spec            = P_dict \
        ( border           = P.border_button
        , cursor           = "pointer"
        , margin           = TRBL0 (t = Em (1./4), b = Em (3./4))
        , padding          = TRBL  (Em (0.5), Em (1.5))
        , ** Border (radius = Px (10))
        )

    col_padding            = Rem (0.3125) ### Px (5)

    background_color       = P.color.p_white
    link_color             = RGB_X     ("#0000EE")
    no_link_color          = RGB_X     ("#333333")
    text_color             = RGB_X     ("#000033")
    visited_color          = RGB_X     ("#551A8B")

    class afs (Definition) :

        block_margin_bottom    = Em (0.1)

        border_spec_input      = Border.P \
            ( color            = P.R.color_dark_grey
            , style            = "solid"
            , width            = Px (1)
            )
        border_spec_readonly   = Border.P \
            ( color            = P.R.color_medium_grey
            , style            = "solid"
            , width            = Px (2)
            )
        border_spec_section    = Border.P \
            ( color            = P.R.color_darker_grey
            , style            = "solid"
            , width            = TRBL0 (l = Px (2), default = Px (1))
            )

        color_spec_desc        = P_dict \
            ( background_color = P.R.color_desc
            , color            = P.R.background_color
            )
        color_spec_heading     = P_dict \
            ( background_color = P.R.color_heading
            , color            = P.R.background_color
            )
        color_spec_heading_closed = P_dict \
            ( background_color = P.R.color_heading_closed
            , color            = P.R.background_color
            )
        color_spec_heading_sub = P_dict \
            ( background_color = P.R.color_heading_sub
            , color            = P.R.background_color
            )
        color_spec_label       = P_dict \
            ( background_color = "inherit"
            , color            = P.R.text_color
            )
        color_spec_optional    = P.R.color_spec_normal
        color_spec_necessary   = P_dict \
            ( background_color = P.R.color_light_grey
            , color            = P.R.text_color
            )
        color_spec_readonly    = P_dict \
            ( background_color = P.R.color_light_grey
            , color            = P.R.color_dark_grey
            )
        color_spec_required    = P_dict \
            ( background_color = P.R.color_medium_grey
            , color            = P.R.text_color
            )

        header_padding         = TRBL (Em (0.2), Em (0.2), Em (0.3), Em (0.5))
        status_size            = Px (12)

    # end class afs

    class breakpoint (Definition) :
        """Breakpoints for responsive rules"""

        really_narrow          = P_dict \
            ( max_width        = Px (360)
            )

        very_narrow            = P_dict \
            ( max_width        = Px (420)
            )

        quite_narrow           = P_dict \
            ( max_width        = Px (480)
            )

        narrow                 = P_dict \
            ( max_width        = Px (680)
            )

        small_device           = P_dict \
            ( max_device_width = Px (767)
            )

        supports_two_column    = P_dict \
            ( min_width        = Px (768)
            )

        broad                  = P_dict \
            ( min_width        = Px (1280)
            )

        wide                   = P_dict \
            ( min_width        = Px (1600)
            )

    # end class breakpoint

    class cal (Definition) :

        date_bg                = P.R.color_medium_grey
        date_padding           = TRBL0 (r = Em (1./4), b = Em (1./10))
        event_bg               = RGB_X ("#FFF8AF")
        font_size              = Em    (0.7)
        line_height            = 1.5
        holiday_bg             = RGB_X ("#CCFFFF")
        month_color            = RGB_X ("#777777")
        weekend_color          = P.R.color.m_blue
        week_bg                = P.R.color_heading
        week_color             = RGB_8 (255, 153, 0)
        week_height            = Em    (8)

    # end class cal

    class menu_icon (Definition) :

        color                  = P.R.color_selected
        line_width             = Rem (0.1875)
        margin_ab              = Em (0.4375)
        margin_m               = Em (0.125)
        width                  = Em  (1.25)

    # end class menu_icon

    class nav (Definition) :

        border_radius              = Em (0.625) ### Px (10)

        class header (Definition) :

            a_color                = P.T.color_target
            a_margin               = 0
            a_padding              = Em (1)

            hbt_sep                = Em (1)

        # end class header

        class main (Definition) :

            a_font_size            = "small"
            a_font_size_current    = Em (0.875)
            background_color       = P.T.background_color

            button_spec            = P_dict \
                ( border           = P.T.border_button
                , color            = P.link_color
                , margin           = 0
                , text_align       = "center"
                )

            color_no_link          = P.T.color_heading
            color_spec_heading     = P_dict \
                ( background_color = P.T.color_heading
                , color            = P.background_color
                )

            color_spec_heading_rev = P_dict \
                ( background_color = P.background_color
                , color            = P.T.color_heading
                )

            color_spec_label       = P_dict \
                ( background_color = P.background_color
                , color            = P.T.text_color
                )

            color_spec_link        = P_dict \
                ( background_color = P.background_color
                , color            = P.link_color
                )
            color_spec_link_current    = P_dict \
                ( background_color = P.T.color_lighter_grey
                , color            = P.T.color_heading
                )

            color_spec_no_link     = P_dict \
                ( background_color = P.background_color
                , color            = P.color_no_link
                , opacity          = 0.7
                )

            color_spec_section_current = P_dict \
                ( background_color = P.background_color
                , color            = P.T.color_heading
                )

            color_spec_visited     = P_dict \
                ( color_spec_link
                , color            = P.visited_color
                )

            color_spec_web_link_hover = P_dict \
                ( background_color = P.link_color
                , color            = P.background_color
                )

            li_left                = Em (0.75)
            line_height_larger     = 1.50
            line_height_normal     = 1.35
            link_color             = P.T.color_selected
            mark_color_link        = P.T.css_arrow_color
            mark_color_section     = P.T.color_heading
            mark_width             = Em (0.40)
            max_button_width       = Em (20)
            padding                = TRBL (Rem (1./4), Rem (0.625), 0)
            visited_color          = P.T.color_heading

            vert_padding           = Rem (0.2)
            width                  = Rem (11.875) + 3 * P.T.col_padding

        # end class main

        class rel (Definition) :

            a_color                = P.T.color_target
            a_margin               = Em (0.5)
            a_padding              = Em (1)

        # end class rel

    # end class nav

    class pure (Definition) :
        """Parameters of `pure` css as of version v0.4.2."""

        input_focus_border_color = RGB_X ("#129FEA")

        label_width              = Em (10.0)
        label_margin_right       = Em (1.0)

        aside_indent             = label_width + label_margin_right

    # end class pure

    class tablesorter (Definition) :

        color_marker           = P.R.background_color
        margin_top             = Px (8)
        opacity                = 0.75
        width                  = Px (5)

    # end class tablesorter

    class Rule (Rule_Definition) :

        clearfix           = Rule_Pseudo \
            ( "after"
            , clear        = "both"
            , content      = "' '"
            , display      = "table"
            # http://nicolasgallagher.com/micro-clearfix-hack/
            )

        disabled           = Rule_Class \
            ( "disabled"
            , opacity      = 0.5
            )

        focus              = Rule_Pseudo \
            ( "focus"
            ,  P.R.color_spec_selected
            )

        focus_outline      = Rule_Pseudo \
            ( "focus"
            ,  P.R.color_spec_selected
            , outline      = P.R.outline_focus
            )

        hidden             = Rule \
            ( display      = "none"
            , visibility   = "hidden"
            )

        hidden_collapse    = Rule \
            ( display      = "none"
            , visibility   = "collapse"
            )

        hover              = Rule_Pseudo \
            ( "hover"
            ,  P.R.color_spec_selected
            )

        hover_rev          = Rule_Pseudo \
            ( "hover"
            ,  P.R.color_spec_selected_rev
            )

        input_focus        = Rule_Pseudo \
            ( "focus"
            , background_color = "inherit"
            , border_color     = P.R.pure.input_focus_border_color
            , color            = RGB_X ("#0078E7")
            , outline          = P.R.pure.input_focus_border_color
            )

        link               = Rule_Pseudo \
            ( "link"
            , color        = P.R.link_color
            )

        main_nav_off       = Rule \
            ( height       = 0
            , padding      = 0
            , width        = 0
            )

        main_nav_on        = Rule \
            ( height       = "auto"
            , padding      = P.R.nav.main.padding
            , width        = "auto"
            )

        rotate_45_left     = Rule \
            ( Transform ("rotate(-45deg)")
            , display          = "inline-block"
            )

        row_even           = Rule_Pseudo \
            ( "nth-child(2n)"
            , P.R.color_spec_row2
            )

        row_odd            = Rule_Pseudo \
            ( "nth-child(2n+1)"
            , P.R.color_spec_row1
            )

        target             = Rule_Pseudo \
            ( "target"
            ,  P.R.color_spec_selected
            )

        target_outline     = Rule_Pseudo \
            ( "target"
            , P.R.color_spec_selected
            , outline      = P.R.outline_focus
            )

        target_visible     = Rule_Pseudo \
            ( "target"
            , visibility   = "visible"
            )

        target_visible_block = Rule_Pseudo \
            ( "target"
            , display      = "block"
            , visibility   = "visible"
            )

        visible            = Rule_Pseudo \
            ( "target"
            , visibility   = "visible"
            )

        visible_block      = Rule_Pseudo \
            ( display      = "block"
            , visibility   = "visible"
            )

        visited            = Rule_Pseudo \
            ( "visited"
            , color        = P.R.visited_color
            )

    # end class Rule

    color_spec_error       = P_dict \
        ( background_color = P.background_color
        , color            = P.color_status_bad
        )
    color_spec_gallery_heading = P_dict \
        ( background_color = RGB_P     (50, 75, 100)
        , color            = P.nav.main.background_color
        )
    color_spec_heading     = P_dict \
        ( background_color = P.background_color
        , color            = P.color_selected
        )
    color_spec_normal      = P_dict \
        ( background_color = P.background_color
        , color            = P.text_color
        )
    color_spec_pg_head     = P_dict \
        ( background_color = P.background_color
        , color            = RGB_X     ("#0200DE")
        )
    color_spec_row1        = color_spec_meta = P_dict \
        ( background_color = "transparent"
        , color            = P.text_color
        )
    color_spec_row2        = color_spec_message = P_dict \
        ( background_color = P.color_lightest_grey
        , color            = P.text_color
        )
    color_spec_selected    = P_dict \
        ( background_color = SVG_Color ("yellow")
        , color            = SVG_Color ("red")
        )
    color_spec_selected_rev= P_dict \
        ( background_color = SVG_Color ("red")
        , color            = SVG_Color ("yellow")
        )
    color_spec_strong      = P_dict \
        ( background_color = P.background_color
        , color            = SVG_Color ("blue")
        )
    color_spec_sub_heading = P_dict \
        ( background_color = P.background_color
        , color            = P.color_half_grey
        )
    color_spec_term        = P_dict \
        ( background_color = RGB_X ("#E6E6E6")
        , color            = P.color_dark_grey
        )

    del_spec               = P_dict \
        ( text_decoration  = "line-through"
        # XXX ???
        )

    font_family_normal     = """"Lucida Grande", verdana, sans-serif"""
    font_family_pre        = \
        """"Lucida Sans Typewriter", "Lucida Console", "Courier New", Courier, monospace"""
    font_family_print      = "serif"
        ### Don't use specific fonts for `print` because font substitution done
        ### by a printer can look terribly ugly
    font_spec_normal       = P_dict \
        ( font_family      = P.font_family_normal
        , font_style       = "normal"
        , font_weight      = "normal"
        , line_height      = P.line_height_normal
        )

    font_spec_print        = P_dict \
        ( font_spec_normal
        , font_family      = P.font_family_print
        )

    font_spec_em           = P_dict \
        ( font_spec_normal
        , font_weight      = "bold"
        )
    font_spec_pre          = P_dict \
        ( font_spec_normal
        , font_family      = P.font_family_pre
        )

    grid_table_border      = "3px ridge gray"

    h1_font_size           = Percent (125)
    h1_font_weight         = "bold"

    hbox_spec              = P_dict \
        ( display          = "block"
        , overflow         = "hidden"
        )

    hr_spec                = P_dict \
        ( border           = 0
        , border_top       = "1px solid #CCC"
        , display          = "block"
        , height           = Px (1)
        , margin           = TRBL (Em (1), 0)
        , padding          = 0
        )

    input_margin           = TRBL (Em (0.1), 0)
    input_padding          = Em (0.2)

    ins_spec               = P_dict \
        ( text_decoration  = "none"
        # XXX ???
        )

    line_height_heading    = 2.00
    line_height_larger     = 1.875
    line_height_normal     = 1.44
    line_height_input      = 1.143

    outline_focus          = "2px solid "   + P.color_focus
    outline_target         = "2px dotted "  + P.color_target

    pg_body_margin_lr      = Em (3.6)
    pg_head_height         = "auto"
    pg_header_nav_height   = Rem (3.5)
    pg_main_max_width      = Em (45)
    pg_main_min_width      = Em (15)
    pg_short_nav_font_size = Rem (1.20)
    pg_short_nav_top       = Em (3)

    thumbnail_size         = Px (155)
    thumbnail_selected_color = P.color_selected

    class Debugger (Definition) :

        background_color           = P.R.background_color
        console_border_color       = P.R.color_border_grey
        console_background_color   = P.R.color_lightest_grey
        console_text_color         = P.R.color.m_black

        form_text_color            = P.R.color_dark_grey

        traceback_background_color = P.R.background_color
        traceback_text_color       = P.R.background_color

    # end class Debugger

# end class Media_Defaults

### __END__ JNJ.Media_Defaults
