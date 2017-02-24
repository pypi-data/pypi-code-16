# -*- coding: utf-8 -*-
# Copyright (C) 2014-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Dingbats
#
# Purpose
#    Dingbats as unicode characters
#
# Revision Dates
#    13-Feb-2014 (CT) Creation
#    20-Feb-2014 (CT) Sort dingbats by name
#    20-Feb-2014 (CT) Add `trigram_for_heaven`
#    13-Mar-2014 (CT) Add some symbols for triangles and blocks
#    23-Jan-2015 (CT) Add some symbols for various space characters
#    29-Jun-2016 (CT) Add `infinity`
#     4-Jan-2017 (CT) Add `white...triangle` symbols (geometric_shapes)
#     4-Jan-2017 (CT) Add some miscellaneous_technical symbols
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _TFL       import TFL

### http://www.unicode.org/charts/PDF/U2700.pdf
### http://www.alanwood.net/unicode/dingbats.html

airplane                                                            = "\u2708"
back_tilted_shadowed_white_rightwards_arrow                         = "\u27ab"
balloon_spoked_asterisk                                             = "\u2749"
ballot_x                                                            = "\u2717"
black_centre_white_star                                             = "\u272c"
black_diamond_minus_white_x                                         = "\u2756"
black_feathered_north_east_arrow                                    = "\u27b6"
black_feathered_rightwards_arrow                                    = "\u27b5"
black_feathered_south_east_arrow                                    = "\u27b4"
black_florette                                                      = "\u273f"
black_four_pointed_star                                             = "\u2726"
black_nib                                                           = "\u2712"
black_question_mark_ornament                                        = "\u2753"
black_rightwards_arrow                                              = "\u27a1"
black_rightwards_arrowhead                                          = "\u27a4"
black_scissors                                                      = "\u2702"
check_mark                                                          = "\u2713"
circled_heavy_white_rightwards_arrow                                = "\u27b2"
circled_open_centre_eight_pointed_star                              = "\u2742"
circled_white_star                                                  = "\u272a"
cross_mark                                                          = "\u274c"
curly_loop                                                          = "\u27b0"
curved_stem_paragraph_sign_ornament                                 = "\u2761"
dashed_triangle_headed_rightwards_arrow                             = "\u279f"
dingbat_circled_sans_serif_digit_eight                              = "\u2787"
dingbat_circled_sans_serif_digit_five                               = "\u2784"
dingbat_circled_sans_serif_digit_four                               = "\u2783"
dingbat_circled_sans_serif_digit_nine                               = "\u2788"
dingbat_circled_sans_serif_digit_one                                = "\u2780"
dingbat_circled_sans_serif_digit_seven                              = "\u2786"
dingbat_circled_sans_serif_digit_six                                = "\u2785"
dingbat_circled_sans_serif_digit_three                              = "\u2782"
dingbat_circled_sans_serif_digit_two                                = "\u2781"
dingbat_circled_sans_serif_number_ten                               = "\u2789"
dingbat_negative_circled_digit_eight                                = "\u277d"
dingbat_negative_circled_digit_five                                 = "\u277a"
dingbat_negative_circled_digit_four                                 = "\u2779"
dingbat_negative_circled_digit_nine                                 = "\u277e"
dingbat_negative_circled_digit_one                                  = "\u2776"
dingbat_negative_circled_digit_seven                                = "\u277c"
dingbat_negative_circled_digit_six                                  = "\u277b"
dingbat_negative_circled_digit_three                                = "\u2778"
dingbat_negative_circled_digit_two                                  = "\u2777"
dingbat_negative_circled_number_ten                                 = "\u277f"
dingbat_negative_circled_sans_serif_digit_eight                     = "\u2791"
dingbat_negative_circled_sans_serif_digit_five                      = "\u278e"
dingbat_negative_circled_sans_serif_digit_four                      = "\u278d"
dingbat_negative_circled_sans_serif_digit_nine                      = "\u2792"
dingbat_negative_circled_sans_serif_digit_one                       = "\u278a"
dingbat_negative_circled_sans_serif_digit_seven                     = "\u2790"
dingbat_negative_circled_sans_serif_digit_six                       = "\u278f"
dingbat_negative_circled_sans_serif_digit_three                     = "\u278c"
dingbat_negative_circled_sans_serif_digit_two                       = "\u278b"
dingbat_negative_circled_sans_serif_number_ten                      = "\u2793"
double_curly_loop                                                   = "\u27bf"
drafting_point_rightwards_arrow                                     = "\u279b"
eight_petalled_outlined_black_florette                              = "\u2741"
eight_pointed_black_star                                            = "\u2734"
eight_pointed_pinwheel_star                                         = "\u2735"
eight_pointed_rectilinear_black_star                                = "\u2737"
eight_spoked_asterisk                                               = "\u2733"
eight_teardrop_spoked_propeller_asterisk                            = "\u274a"
envelope                                                            = "\u2709"
floral_heart                                                        = "\u2766"
four_balloon_spoked_asterisk                                        = "\u2723"
four_club_spoked_asterisk                                           = "\u2725"
four_teardrop_spoked_asterisk                                       = "\u2722"
front_tilted_shadowed_white_rightwards_arrow                        = "\u27ac"
heavy_asterisk                                                      = "\u2731"
heavy_ballot_x                                                      = "\u2718"
heavy_black_curved_downwards_and_rightwards_arrow                   = "\u27a5"
heavy_black_curved_upwards_and_rightwards_arrow                     = "\u27a6"
heavy_black_feathered_north_east_arrow                              = "\u27b9"
heavy_black_feathered_rightwards_arrow                              = "\u27b8"
heavy_black_feathered_south_east_arrow                              = "\u27b7"
heavy_black_heart                                                   = "\u2764"
heavy_check_mark                                                    = "\u2714"
heavy_chevron_snowflake                                             = "\u2746"
heavy_concave_pointed_black_rightwards_arrow                        = "\u27a8"
heavy_dashed_triangle_headed_rightwards_arrow                       = "\u27a0"
heavy_division_sign                                                 = "\u2797"
heavy_double_comma_quotation_mark_ornament                          = "\u275e"
heavy_double_turned_comma_quotation_mark_ornament                   = "\u275d"
heavy_eight_pointed_rectilinear_black_star                          = "\u2738"
heavy_eight_teardrop_spoked_propeller_asterisk                      = "\u274b"
heavy_exclamation_mark_ornament                                     = "\u2762"
heavy_exclamation_mark_symbol                                       = "\u2757"
heavy_four_balloon_spoked_asterisk                                  = "\u2724"
heavy_greek_cross                                                   = "\u271a"
heavy_heart_exclamation_mark_ornament                               = "\u2763"
heavy_left_pointing_angle_bracket_ornament                          = "\u2770"
heavy_left_pointing_angle_quotation_mark_ornament                   = "\u276e"
heavy_low_double_comma_quotation_mark_ornament                      = "\u2760"
heavy_low_single_comma_quotation_mark_ornament                      = "\u275f"
heavy_lower_right_shadowed_white_rightwards_arrow                   = "\u27ad"
heavy_minus_sign                                                    = "\u2796"
heavy_multiplication_x                                              = "\u2716"
heavy_north_east_arrow                                              = "\u279a"
heavy_open_centre_cross                                             = "\u271c"
heavy_outlined_black_star                                           = "\u272e"
heavy_plus_sign                                                     = "\u2795"
heavy_right_pointing_angle_bracket_ornament                         = "\u2771"
heavy_right_pointing_angle_quotation_mark_ornament                  = "\u276f"
heavy_rightwards_arrow                                              = "\u2799"
heavy_round_tipped_rightwards_arrow                                 = "\u279c"
heavy_single_comma_quotation_mark_ornament                          = "\u275c"
heavy_single_turned_comma_quotation_mark_ornament                   = "\u275b"
heavy_south_east_arrow                                              = "\u2798"
heavy_sparkle                                                       = "\u2748"
heavy_teardrop_shanked_rightwards_arrow                             = "\u27bb"
heavy_teardrop_spoked_asterisk                                      = "\u273d"
heavy_teardrop_spoked_pinwheel_asterisk                             = "\u2743"
heavy_triangle_headed_rightwards_arrow                              = "\u279e"
heavy_upper_right_shadowed_white_rightwards_arrow                   = "\u27ae"
heavy_vertical_bar                                                  = "\u275a"
heavy_wedge_tailed_rightwards_arrow                                 = "\u27bd"
heavy_wide_headed_rightwards_arrow                                  = "\u2794"
latin_cross                                                         = "\u271d"
left_shaded_white_rightwards_arrow                                  = "\u27aa"
light_left_tortoise_shell_bracket_ornament                          = "\u2772"
light_right_tortoise_shell_bracket_ornament                         = "\u2773"
light_vertical_bar                                                  = "\u2758"
lower_blade_scissors                                                = "\u2703"
lower_right_drop_shadowed_white_square                              = "\u274f"
lower_right_pencil                                                  = "\u270e"
lower_right_shadowed_white_square                                   = "\u2751"
maltese_cross                                                       = "\u2720"
medium_flattened_left_parenthesis_ornament                          = "\u276a"
medium_flattened_right_parenthesis_ornament                         = "\u276b"
medium_left_curly_bracket_ornament                                  = "\u2774"
medium_left_parenthesis_ornament                                    = "\u2768"
medium_left_pointing_angle_bracket_ornament                         = "\u276c"
medium_right_curly_bracket_ornament                                 = "\u2775"
medium_right_parenthesis_ornament                                   = "\u2769"
medium_right_pointing_angle_bracket_ornament                        = "\u276d"
medium_vertical_bar                                                 = "\u2759"
multiplication_x                                                    = "\u2715"
negative_squared_cross_mark                                         = "\u274e"
notched_lower_right_shadowed_white_rightwards_arrow                 = "\u27af"
notched_upper_right_shadowed_white_rightwards_arrow                 = "\u27b1"
open_centre_asterisk                                                = "\u2732"
open_centre_black_star                                              = "\u272b"
open_centre_cross                                                   = "\u271b"
open_centre_teardrop_spoked_asterisk                                = "\u273c"
open_outlined_rightwards_arrow                                      = "\u27be"
outlined_black_star                                                 = "\u272d"
outlined_greek_cross                                                = "\u2719"
outlined_latin_cross                                                = "\u271f"
pencil                                                              = "\u270f"
pinwheel_star                                                       = "\u272f"
raised_fist                                                         = "\u270a"
raised_hand                                                         = "\u270b"
right_shaded_white_rightwards_arrow                                 = "\u27a9"
rotated_floral_heart_bullet                                         = "\u2767"
rotated_heavy_black_heart_bullet                                    = "\u2765"
shadowed_white_circle                                               = "\u274d"
shadowed_white_latin_cross                                          = "\u271e"
shadowed_white_star                                                 = "\u2730"
six_petalled_black_and_white_florette                               = "\u273e"
six_pointed_black_star                                              = "\u2736"
sixteen_pointed_asterisk                                            = "\u273a"
snowflake                                                           = "\u2744"
sparkle                                                             = "\u2747"
sparkles                                                            = "\u2728"
squat_black_rightwards_arrow                                        = "\u27a7"
star_of_david                                                       = "\u2721"
stress_outlined_white_star                                          = "\u2729"
tape_drive                                                          = "\u2707"
teardrop_barbed_rightwards_arrow                                    = "\u27ba"
teardrop_spoked_asterisk                                            = "\u273b"
telephone_location_sign                                             = "\u2706"
three_d_bottom_lighted_rightwards_arrowhead                         = "\u27a3"
three_d_top_lighted_rightwards_arrowhead                            = "\u27a2"
tight_trifoliate_snowflake                                          = "\u2745"
triangle_headed_rightwards_arrow                                    = "\u279d"
twelve_pointed_black_star                                           = "\u2739"
upper_blade_scissors                                                = "\u2701"
upper_right_drop_shadowed_white_square                              = "\u2750"
upper_right_pencil                                                  = "\u2710"
upper_right_shadowed_white_square                                   = "\u2752"
victory_hand                                                        = "\u270c"
wedge_tailed_rightwards_arrow                                       = "\u27bc"
white_exclamation_mark_ornament                                     = "\u2755"
white_feathered_rightwards_arrow                                    = "\u27b3"
white_florette                                                      = "\u2740"
white_four_pointed_star                                             = "\u2727"
white_heavy_check_mark                                              = "\u2705"
white_nib                                                           = "\u2711"
white_question_mark_ornament                                        = "\u2754"
white_scissors                                                      = "\u2704"
writing_hand                                                        = "\u270d"

### technically not dingbats

### http://www.alanwood.net/unicode/geometric_shapes.html
black_circle                                                        = "\u25CF"
black_down_pointing_triangle                                        = "\u25BC"
black_left_pointing_triangle                                        = "\u25C0"
black_lower_left_triangle                                           = "\u25E3"
black_lower_right_triangle                                          = "\u25E2"
black_right_pointing_triangle                                       = "\u25B6"
black_up_pointing_triangle                                          = "\u25B2"
black_upper_left_triangle                                           = "\u25E4"
black_upper_right_triangle                                          = "\u25E5"

white_down_pointing_triangle                                        = "\u25BD"
white_left_pointing_triangle                                        = "\u25C1"
white_lower_left_triangle                                           = "\u25FA"
white_lower_right_triangle                                          = "\u25FF"
white_right_pointing_triangle                                       = "\u25B7"
white_up_pointing_triangle                                          = "\u25B3"
white_upper_left_triangle                                           = "\u25F8"
white_upper_right_triangle                                          = "\u25F9"

### http://www.alanwood.net/unicode/block_elements.html
left_one_eighth_block                                               = "\u258F"
left_one_quarter_block                                              = "\u258E"
right_one_eighth_block                                              = "\u2595"

### http://www.alanwood.net/unicode/mathematical_operators.html
infinity                                                            = "\u221E"

### http://www.alanwood.net/unicode/miscellaneous_symbols.html
trigram_for_heaven                                                  = "\u2630"

### http://www.alanwood.net/unicode/miscellaneous_technical.html
house                                                               = "\u2302"
up_arrowhead                                                        = "\u2303"
down_arrowhead                                                      = "\u2304"
left_pointing_angle_bracket                                         = "\u2329"
right_pointing_angle_bracket                                        = "\u232A"

### various space characters
figure_space                                                        = "\u2007"
narrow_no_break_space                                               = "\u202F"
no_break_space                                                      = "\u00A0"
thin_space                                                          = "\u2009"
zero_width_space                                                    = "\u200B"

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Dingbats
