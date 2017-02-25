# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    JNJ.Environment
#
# Purpose
#    Provide wrapper around jinja2.Environment
#
# Revision Dates
#    29-Dec-2009 (CT) Creation
#    13-Jan-2010 (CT) `GTW` converted from module to class instance
#    21-Jan-2010 (MG) `I18N` support added
#    21-Jan-2010 (CT) Bugs fixed
#    22-Jan-2010 (CT) PrefixLoader for `STD::` added to allow access
#                     to shadowed templates of JNJ itself
#    23-Feb-2010 (MG) `Default_Extensions` factored
#     3-Jan-2011 (CT) `CSS_Parameters` added
#    16-Mar-2011 (CT) Optional argument `GTW` added to `HTML`
#    29-Mar-2012 (CT) Rename `CSS_Parameters` to `Media_Parameters`
#    18-Nov-2013 (CT) Change default `encoding` to `utf-8`
#     9-Jul-2014 (CT) Add `prefixes` argument to `HTML`
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _JNJ               import JNJ
from   _TFL               import TFL

import _JNJ.Onion
import _JNJ.GTW

from   _TFL               import sos
from   _TFL.predicate     import uniq
from   _TFL.pyk           import pyk
import _TFL.I18N

from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PrefixLoader

Default_Extensions = ["jinja2.ext.loopcontrols", "jinja2.ext.do", JNJ.Onion]

def HTML \
        ( version          = "html/5.jnj"
        , load_path        = ()
        , loader           = None
        , globals          = {}
        , encoding         = "utf-8"
        , i18n             = False
        , Media_Parameters = None
        , GTW              = None
        , prefixes         = {}
        , ** kw
        ) :
    jnj_loader = FileSystemLoader (sos.path.dirname (__file__), "utf-8")
    loaders    = []
    if loader :
        loaders.append (loader)
    if load_path :
        loaders.append (FileSystemLoader (load_path, encoding))
    loaders.append (jnj_loader)
    if prefixes :
        sk = lambda x : (- len (x [1]), x [1])
        for prefix, lp in sorted (pyk.iteritems (prefixes), key = sk) :
            loaders.append \
                ( PrefixLoader
                   ({prefix : FileSystemLoader (lp, encoding)}, delimiter='::')
                )
    loaders.append (PrefixLoader (dict (STD = jnj_loader), delimiter='::'))
    loader     = ChoiceLoader (loaders)
    extensions = (kw.pop ("extensions", []) + Default_Extensions)
    if i18n :
        extensions.append ("jinja2.ext.i18n")
    result = Environment  \
        ( extensions = uniq (extensions), loader = loader, ** kw)
    if GTW is None :
        GTW = JNJ.GTW (result)
    result.globals.update \
        ( globals
        , GTW          = GTW
        , html_version = version
        )
    result.Media_Parameters = Media_Parameters
    result.encoding         = encoding
    result.static_handler   = None
    if i18n :
        result.install_gettext_translations (TFL.I18N)
    return result
# end def HTML

__doc__ = """
`HTML` creates an environment suitable for generating HTML from jinja
templates. Per default, `HTML` sets `html_version` to a macro template
for HTML5.

    >>> env5 = HTML ()

Passing `version = "html/x.jnj"` to `HTML` sets up an environment with
`html_version` referring to a macro template for XHTML.

    >>> envx = HTML (version = "html/x.jnj")

By importing `html_version` as `x` and calling macros defined by `X`,
a single template can generate either HTML5 or XHTML output, depending
on how the environment was set up::

    >>> template = '''
    ... {%- import html_version as X -%}
    ... {%- call X.html (lang = "de") -%}
    ...   {%- call X.section (id = "foo", class = "bar") -%}
    ...     A sample section for testing the differences between
    ...     html5 and xhtml.
    ...   {%- endcall -%}
    ...
    ...   {%- set a = None %}
    ...   {%- set b = 42 %}
    ...   {%- set c = "cccc" %}
    ...   {{ GTW.firstof (a, b, c, d, "default first of") }}
    ...   {{ GTW.firstof (b, c, d, "default first of") }}
    ...   {{ GTW.firstof (c, d, "default first of") }}
    ...   {{ GTW.firstof (d, "default first of") }}
    ...   {{ GTW.firstof ("default first of") }}
    ...
    ...   {{ X.input.textarea (80, 5, value = "Wing is king", class = "fast") }}
    ...
    ...   {{ X.input.select ("Choice", ["red", "green"], class = "side") }}
    ...   {{ X.input.select_v ("CV", [(0, "red"), (1, "green")], 1, class = "side") }}
    ... {%- endcall -%}
    ... '''

    >>> t5 = env5.from_string (template)
    >>> print (t5.render ().replace ('<section id="foo" class="bar">', '<section class="bar" id="foo">'))
    <!DOCTYPE html>
    <html lang="de" class="no-js">
      <section class="bar" id="foo">
      A sample section for testing the differences between
        html5 and xhtml.
    </section>
      42
      42
      cccc
      default first of
      default first of
    <BLANKLINE>
      <textarea cols="80" rows="5" class="fast">Wing is king</textarea>
    <BLANKLINE>
    <BLANKLINE>
      <select class="side" name="Choice">
    <BLANKLINE>
          <option value="">---</option>
    <BLANKLINE>
            <option>red</option>
    <BLANKLINE>
            <option>green</option>
    <BLANKLINE>
        </select>
    <BLANKLINE>
      <select class="side" name="CV">
    <BLANKLINE>
    <BLANKLINE>
            <option value="0">red</option>
            <option value="1" selected="selected">green</option>
    <BLANKLINE>
            <option value="">---</option>
        </select>
    </html>

    >>> et = env5.get_template ("email/email.jnj")
    >>> print (et.render (email_from = "tanzer@swing.co.at", email_to = "martin@mangari.com", email_body = "Nih!", NAV = None))
    From:    tanzer@swing.co.at
    To:      martin@mangari.com
    Content-type: text/plain; charset=iso-8859-15
    <BLANKLINE>
    <BLANKLINE>
    Nih!

    >>> print (et.render (email_from = "tanzer@swing.co.at", email_to = "martin@mangari.com", email_body = "Nih!", NAV = None))
    From:    tanzer@swing.co.at
    To:      martin@mangari.com
    Content-type: text/plain; charset=iso-8859-15
    <BLANKLINE>
    <BLANKLINE>
    Nih!

"""

if __name__ != "__main__" :
    JNJ._Export_Module ()
### __END__ JNJ.Environment
