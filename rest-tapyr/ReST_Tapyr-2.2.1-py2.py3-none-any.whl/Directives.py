# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package ReST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    ReST.Directives
#
# Purpose
#    Define some directives for reStructuredText
#
# Revision Dates
#    21-Feb-2012 (CT) Creation
#    27-Nov-2015 (CT) Fix `option_spec` for `align`
#    11-Oct-2016 (CT) Change `GTW.HTML` to `TFL.HTML`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _ReST                                  import ReST
from   _TFL                                   import TFL

from   docutils                               import nodes
from   docutils.parsers.rst                   import directives
from   docutils.parsers.rst                   import Directive
from   docutils.parsers.rst.directives.images import Image

class _Video_ (Directive) :

    required_arguments        = 1
    optional_arguments        = 0
    final_argument_whitespace = True
    option_spec               = dict \
        ( { 'class'           : directives.class_option
          }
        , align               = directives.unchanged
        , autoplay            = directives.flag
        , desc                = directives.unchanged
        , height              = directives.nonnegative_int
        , loop                = directives.flag
        , width               = directives.nonnegative_int
        )
    has_content               = False

    def run (self) :
        video_id = self.arguments [0]
        kw       = dict (self.options)
        if "class" in kw :
            kw ["css_class"] = " ".join (kw.pop ("class"))
        html = self.runner (video_id, ** kw)
        return [nodes.raw ("", html, format='html')]
    # end def run

# end class _Video_

class Vimeo (_Video_) :

    option_spec              = dict \
        ( _Video_.option_spec
        , title               = directives.flag
        )

    @property
    def runner (self) :
        from _TFL.HTML import vimeo_video
        return TFL.HTML.vimeo_video
    # end def runner

# end class Vimeo

class Youtube (_Video_) :

    option_spec              = dict \
        ( _Video_.option_spec
        , autohide           = lambda arg: directives.choice (arg, (0, 1, 2))
        , controls           = directives.flag
        , fs                 = directives.flag
        , hd                 = directives.flag
        )

    @property
    def runner (self) :
        from _TFL.HTML import youtube_video
        return youtube_video
    # end def runner

# end class Youtube

directives.register_directive ("vimeo",   Vimeo)
directives.register_directive ("youtube", Youtube)

### __END__ ReST.Directives
