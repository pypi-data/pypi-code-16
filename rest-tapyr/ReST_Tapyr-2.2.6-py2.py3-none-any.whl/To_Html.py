# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package ReST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    ReST.To_Html
#
# Purpose
#    Convert re-structured text to HTML
#
# Revision Dates
#    17-Mar-2010 (CT) Creation
#    22-Feb-2012 (CT) Import `_ReST.Directives`
#    21-Apr-2015 (CT) Disable `file_insertion_enabled`, `raw_enabled`
#    10-Jul-2015 (CT) Add `logging` for exceptions raised by docutils
#    10-Jul-2015 (CT) Patch `get_measure` broken in docutils versions < 0.11
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _ReST                    import ReST
from   _TFL                     import TFL

import _ReST.Roles
import _ReST.Directives

from   _TFL.predicate           import uniq
from   _TFL.pyk                 import pyk
from   _TFL._Meta.Once_Property import Once_Property

import _TFL._Meta.Object

import itertools
import logging

class To_Html (TFL.Meta.Object) :
    """Convert re-structured text to HTML."""

    include  = ("html_title", "html_subtitle", "fragment")

    ### http://docutils.sourceforge.net/docs/user/config.html
    ### http://docutils.sourceforge.net/docs/howto/security.html
    settings = dict \
        ( cloak_email_addresses         = False
        , embed_stylesheet              = False
        , file_insertion_enabled        = False
        , initial_header_level          = "2"
        , input_encoding                = "unicode"
        , language_code                 = "en"
        , output_encoding               = "utf8"
        , output_encoding_error_handler = "xmlcharrefreplace"
        , raw_enabled                   = False
        , smart_quotes                  = False
        , _disable_config               = True
        )

    def __init__ (self, * replacers, ** kw) :
        self.include   = kw.pop ("include", self.include)
        self.replacers = list   (replacers)
        self.settings  = dict   (self.settings, ** kw)
    # end def __init__

    def __call__ (self, txt, encoding = "utf8", language = "en", include = None, ** kw) :
        settings = dict \
            ( self.settings
            , output_encoding = encoding
            , language_code   = language
            , ** kw
            )
        try :
            text  = pyk.decoded (txt)
            parts = self._publish_parts \
                ( source             = text
                , writer_name        = "html4css1"
                , settings_overrides = settings
                )
        except Exception as exc :
            msg = \
                ( _T ( "Conversion from re-structured text to html "
                       "failed with exception:\n    %s"
                     )
                % (exc, )
                )
            logging.exception (msg + "\n\n  Offending text:" + text)
            raise ValueError  (msg)
        if include is None :
            include = self.include
        result = "\n".join (p for p in (parts [i] for i in include) if p)
        for rep in self.replacers :
            result = rep (result)
        return result
    # end def __call__

    def add_replacers (self, * replacers) :
        self.replacers = list \
            (uniq (itertools.chain (self.replacers, replacers)))
    # end def add_replacers

    @Once_Property
    def _publish_parts (self) :
        import _ReST.Roles
        from   docutils.core import publish_parts
        _patch_get_measure ()
        return publish_parts
    # end def _publish_parts

# end class To_Html

def _patch_get_measure () :
    import docutils
    du_version = tuple (int (i) for i in docutils.__version__.split ("."))
    if du_version < (0, 11) :
        ### before 0.11, docutils.parsers.rst.directives.get_measure was broken
        ### for python runs with `-O` because it depended on an `assert`
        ### statement that was optimized away
        ### --> fix this here
        from docutils.parsers.rst import directives
        broken_get_measure = directives.get_measure
        def get_measure (argument, units) :
            try :
                return broken_get_measure (argument, units)
            except AttributeError :
                raise ValueError \
                    ( 'not a positive measure of one of the following units'
                      ':\n%s'
                    % ' '.join(['"%s"' % i for i in units])
                    )
        directives.get_measure = get_measure
# end def _patch_get_measure

to_html = To_Html ()

__doc__ = """
    >>> text = u'''
    ... Test of ReST.to_html
    ... ====================
    ...
    ... Section
    ... -------
    ...
    ... A paragraph by any other name.
    ...
    ... Another section
    ... ---------------
    ...
    ... With another paragraph.
    ...
    ... The end...
    ... '''
    >>> print (ReST.to_html (text, encoding = "utf-8"))
    <h1 class="title">Test of ReST.to_html</h1>
    <BLANKLINE>
    <div class="section" id="section">
    <h2>Section</h2>
    <p>A paragraph by any other name.</p>
    </div>
    <div class="section" id="another-section">
    <h2>Another section</h2>
    <p>With another paragraph.</p>
    <p>The end...</p>
    </div>

    >>> img_text = '''
    ... .. image:: /some/where/pic.jpg
    ...  :alt: Some description
    ...  :class: align-right
    ...  :width: 160
    ...  :target: /some/where/else/target.html
    ... '''
    >>> print (ReST.to_html (img_text, encoding = "utf-8"))
    <a class="reference external image-reference" href="/some/where/else/target.html"><img alt="Some description" class="align-right" src="/some/where/pic.jpg" style="width: 160px;" /></a>
    <BLANKLINE>

"""

if __name__ != "__main__" :
    ReST._Export ("*")
### __END__ ReST.To_Html
