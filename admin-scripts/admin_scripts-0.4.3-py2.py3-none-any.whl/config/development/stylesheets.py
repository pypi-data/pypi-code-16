#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Administration Scripts
# Copyright (c) 2008-2017 Hive Solutions Lda.
#
# This file is part of Hive Administration Scripts.
#
# Hive Administration Scripts is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Administration Scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Administration Scripts. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt> & Luís Martinho <lmartinho@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

configurations = (
    {
        "recursive" : True,
        "windows_newline" : True,
        "fix_extra_newlines" : True,
        "property_order" : (
            "animation",
            "-o-animation",
            "-ms-animation",
            "-moz-animation",
            "-khtml-animation",
            "-webkit-animation",
            "animation-delay",
            "-o-animation-delay",
            "-ms-animation-delay",
            "-moz-animation-delay",
            "-khtml-animation-delay",
            "-webkit-animation-delay",
            "animation-duration",
            "-o-animation-duration",
            "-ms-animation-duration",
            "-moz-animation-duration",
            "-khtml-animation-duration",
            "-webkit-animation-duration",
            "animation-name",
            "-o-animation-name",
            "-ms-animation-name",
            "-moz-animation-name",
            "-khtml-animation-name",
            "-webkit-animation-name",
            "appearance",
            "-o-appearance",
            "-ms-appearance",
            "-moz-appearance",
            "-khtml-appearance",
            "-webkit-appearance",
            "azimuth",
            "backface-visibility",
            "-o-backface-visibility",
            "-ms-backface-visibility",
            "-moz-backface-visibility",
            "-khtml-backface-visibility",
            "-webkit-backface-visibility",
            "background",
            "background-attachment",
            "background-clip",
            "-o-background-clip",
            "-ms-background-clip",
            "-moz-background-clip",
            "-khtml-background-clip",
            "-webkit-background-clip",
            "background-color",
            "background-image",
            "background-origin",
            "background-position",
            "background-position-x",
            "background-position-y",
            "background-size",
            "background-repeat",
            "border",
            "border-bottom",
            "border-bottom-color",
            "border-bottom-left-radius",
            "-o-border-bottom-left-radius",
            "-ms-border-bottom-left-radius",
            "-moz-border-bottom-left-radius",
            "-khtml-border-bottom-left-radius",
            "-webkit-border-bottom-left-radius",
            "border-bottom-right-radius",
            "-o-border-bottom-right-radius",
            "-ms-border-bottom-right-radius",
            "-moz-border-bottom-right-radius",
            "-khtml-border-bottom-right-radius",
            "-webkit-border-bottom-right-radius",
            "border-bottom-style",
            "border-bottom-width",
            "border-collapse",
            "border-color",
            "border-left",
            "border-left-color",
            "border-left-style",
            "border-left-width",
            "border-radius",
            "-o-border-radius",
            "-ms-border-radius",
            "-moz-border-radius",
            "-khtml-border-radius",
            "-webkit-border-radius",
            "-moz-border-radius-bottomleft",
            "-moz-border-radius-bottomright",
            "-moz-border-radius-topleft",
            "-moz-border-radius-topright",
            "border-right",
            "border-right-color",
            "border-right-style",
            "border-right-width",
            "border-spacing",
            "border-style",
            "border-top",
            "border-top-color",
            "border-top-left-radius",
            "-o-border-top-left-radius",
            "-ms-border-top-left-radius",
            "-moz-border-top-left-radius",
            "-khtml-border-top-left-radius",
            "-webkit-border-top-left-radius",
            "border-top-right-radius",
            "-o-border-top-right-radius",
            "-ms-border-top-right-radius",
            "-moz-border-top-right-radius",
            "-khtml-border-top-right-radius",
            "-webkit-border-top-right-radius",
            "border-top-style",
            "border-top-width",
            "border-width",
            "bottom",
            "box-shadow",
            "-o-box-shadow",
            "-ms-box-shadow",
            "-moz-box-shadow",
            "-khtml-box-shadow",
            "-webkit-box-shadow",
            "box-sizing",
            "-o-box-sizing",
            "-ms-box-sizing",
            "-moz-box-sizing",
            "-khtml-box-sizing",
            "-webkit-box-sizing",
            "caption-side",
            "clear",
            "clip",
            "color",
            "column-count",
            "-o-column-count",
            "-ms-column-count",
            "-moz-column-count",
            "-khtml-column-count",
            "-webkit-column-count",
            "column-gap",
            "-o-column-gap",
            "-ms-column-gap",
            "-moz-column-gap",
            "-khtml-column-gap",
            "-webkit-column-gap",
            "content",
            "counter-increment",
            "counter-reset",
            "cue-after",
            "cue-before",
            "cue",
            "cursor",
            "direction",
            "display",
            "elevation",
            "empty-cells",
            "filter",
            "-o-filter",
            "-ms-filter",
            "-moz-filter",
            "-khtml-filter",
            "-webkit-filter",
            "float",
            "font-family",
            "font-size",
            "font-size-adjust",
            "font-smooth",
            "font-smoothing",
            "-o-font-smoothing",
            "-ms-font-smoothing",
            "-moz-font-smoothing",
            "-khtml-font-smoothing",
            "-webkit-font-smoothing",
            "font-style",
            "font-variant",
            "font-weight",
            "font",
            "height",
            "hyphens",
            "-o-hyphens",
            "-ms-hyphens",
            "-moz-hyphens",
            "-khtml-hyphens",
            "-webkit-hyphens",
            "left",
            "letter-spacing",
            "line-height",
            "list-style",
            "list-style-image",
            "list-style-position",
            "list-style-type",
            "margin",
            "margin-bottom",
            "margin-left",
            "margin-right",
            "margin-top",
            "max-height",
            "max-width",
            "min-height",
            "min-width",
            "opacity",
            "-o-opacity",
            "-ms-opacity",
            "-moz-opacity",
            "-khtml-opacity",
            "-webkit-opacity",
            "orphans",
            "osx-font-smoothing",
            "-o-osx-font-smoothing",
            "-ms-osx-font-smoothing",
            "-moz-osx-font-smoothing",
            "-khtml-osx-font-smoothing",
            "-webkit-osx-font-smoothing",
            "outline-color",
            "outline-offset",
            "outline-style",
            "outline-width",
            "outline",
            "-o-outline",
            "-ms-outline",
            "-moz-outline",
            "-khtml-outline",
            "-webkit-outline",
            "overflow",
            "overflow-scrolling",
            "-o-overflow-scrolling",
            "-ms-overflow-scrolling",
            "-moz-overflow-scrolling",
            "-khtml-overflow-scrolling",
            "-webkit-overflow-scrolling",
            "overflow-x",
            "overflow-y",
            "padding-bottom",
            "padding-left",
            "padding-right",
            "padding-top",
            "padding",
            "page-break-after",
            "page-break-before",
            "page-break-inside",
            "pause-after",
            "pause-before",
            "pause",
            "perspective",
            "-o-perspective",
            "-ms-perspective",
            "-moz-perspective",
            "-khtml-perspective",
            "-webkit-perspective",
            "pitch-range",
            "pitch",
            "play-during",
            "print-color-adjust",
            "-o-print-color-adjust",
            "-ms-print-color-adjust",
            "-moz-print-color-adjust",
            "-khtml-print-color-adjust",
            "-webkit-print-color-adjust",
            "pointer-events",
            "position",
            "quotes",
            "resize",
            "richness",
            "right",
            "size",
            "speak",
            "speak-header",
            "speak-numeral",
            "speak-punctuation",
            "speech-rate",
            "src",
            "stress",
            "tab-size",
            "-o-tab-size",
            "-moz-tab-size",
            "table-layout",
            "tap-highlight-color",
            "-o-tap-highlight-color",
            "-ms-tap-highlight-color",
            "-moz-tap-highlight-color",
            "-khtml-tap-highlight-color",
            "-webkit-tap-highlight-color",
            "text-align",
            "text-decoration",
            "text-fill-color",
            "-o-text-fill-color",
            "-ms-text-fill-color",
            "-moz-text-fill-color",
            "-khtml-text-fill-color",
            "-webkit-text-fill-color",
            "text-indent",
            "text-overflow",
            "text-shadow",
            "-o-text-shadow",
            "-ms-text-shadow",
            "-moz-text-shadow",
            "-khtml-text-shadow",
            "-webkit-text-shadow",
            "text-transform",
            "top",
            "touch-callout",
            "-o-touch-callout",
            "-ms-touch-callout",
            "-moz-touch-callout",
            "-khtml-touch-callout",
            "-webkit-touch-callout",
            "transform",
            "-o-transform",
            "-ms-transform",
            "-moz-transform",
            "-khtml-transform",
            "-webkit-transform",
            "transform-origin",
            "-o-transform-origin",
            "-ms-transform-origin",
            "-moz-transform-origin",
            "-khtml-transform-origin",
            "-webkit-transform-origin",
            "transform-style",
            "-o-transform-style",
            "-ms-transform-style",
            "-moz-transform-style",
            "-khtml-transform-style",
            "-webkit-transform-style",
            "transition",
            "-o-transition",
            "-ms-transition",
            "-moz-transition",
            "-khtml-transition",
            "-webkit-transition",
            "transition-delay",
            "-o-transition-delay",
            "-ms-transition-delay",
            "-moz-transition-delay",
            "-khtml-transition-delay",
            "-webkit-transition-delay",
            "transition-duration",
            "-o-transition-duration",
            "-ms-transition-duration",
            "-moz-transition-duration",
            "-khtml-transition-duration",
            "-webkit-transition-duration",
            "transition-timing-function",
            "-o-transition-timing-function",
            "-ms-transition-timing-function",
            "-moz-transition-timing-function",
            "-khtml-transition-timing-function",
            "-webkit-transition-timing-function",
            "unicode-bidi",
            "user-select",
            "-o-user-select",
            "-ms-user-select",
            "-moz-user-select",
            "-khtml-user-select",
            "-webkit-user-select",
            "vertical-align",
            "visibility",
            "voice-family",
            "volume",
            "white-space",
            "widows",
            "width",
            "word-break",
            "word-spacing",
            "word-wrap",
            "z-index",
            "zoom",
            "-o-zoom",
            "-ms-zoom",
            "-moz-zoom",
            "-khtml-zoom",
            "-webkit-zoom"
        ),
        "rules_skip" : (
            "@-",
        ),
        "file_extensions" : (
            "css",
        ),
        "file_exclusion" : ("android-sdk",)
    },
)
