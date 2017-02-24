# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    JNJ.Onion
#
# Purpose
#    Provide Jinja extension for a `onion` tag
#
# Revision Dates
#    29-Dec-2009 (CT) Creation
#    12-Oct-2014 (CT) Use `next` function, not method (Python-3 compatibility)
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    11-Dec-2015 (CT) Fix doc-string of `Onion`
#    ««revision-date»»···
#--

from   _JNJ               import JNJ

from   jinja2     import nodes
from   jinja2.ext import Extension

class Onion (Extension) :
    """Jinja extension providing a `onion` tag.

       >>> from _JNJ.Environment import HTML
       >>> from _TFL.portable_repr import portable_repr
       >>> env = HTML ()
       >>> template = '''
       ...   {%- onion foo %}
       ...     {% head %}
       ...       I am the onion then head
       ...     {% else %}
       ...       I am the onion else head
       ...     {% body %}
       ...       And this is the body which should be enclosed by the head/tail
       ...     {% tail %}
       ...       I am the onion then tail
       ...     {% else %}
       ...       I am the onion else tail
       ...   {% endonion -%}
       ... '''
       >>> t = env.from_string (template)
       >>> print (portable_repr (t.render (foo = True)))
       '\\n      I am the onion then head\\n    \\n      And this is the body which should be enclosed by the head/tail\\n    \\n      I am the onion then tail\\n    '
       >>> print (portable_repr (t.render (foo = False)))
       '\\n      I am the onion else head\\n    \\n      And this is the body which should be enclosed by the head/tail\\n    \\n      I am the onion else tail\\n  '

       The else tags inside the head/tail are optional:

       >>> template = '''
       ...   {%- onion foo %}
       ...     {% head %}
       ...       I am the onion then head
       ...     {% body %}
       ...       And this is the body which should be enclosed by the head/tail
       ...     {% tail %}
       ...       I am the onion then tail
       ...     {% else %}
       ...       I am the onion else tail
       ...   {% endonion -%}
       ... '''
       >>> t = env.from_string (template)
       >>> print (portable_repr (t.render (foo = True)))
       '\\n      I am the onion then head\\n    \\n      And this is the body which should be enclosed by the head/tail\\n    \\n      I am the onion then tail\\n    '
       >>> print (portable_repr (t.render (foo = False)))
       '\\n      And this is the body which should be enclosed by the head/tail\\n    \\n      I am the onion else tail\\n  '
       >>> template = '''
       ...   {% onion foo %}
       ...     {% head %}
       ...       I am the onion then head
       ...     {% else %}
       ...       I am the onion else head
       ...     {% body %}
       ...       And this is the body which should be enclosed by the head/tail
       ...     {% tail %}
       ...       I am the onion then tail
       ...   {% endonion %}
       ... '''.strip ()
       >>> t = env.from_string (template)
       >>> print (portable_repr (t.render (foo = True)))
       '\\n      I am the onion then head\\n    \\n      And this is the body which should be enclosed by the head/tail\\n    \\n      I am the onion then tail\\n  '
       >>> print (portable_repr (t.render (foo = False)))
       '\\n      I am the onion else head\\n    \\n      And this is the body which should be enclosed by the head/tail\\n    '
    """

    tags = set (("onion", ))

    def parse (self, parser) :
        tag    = parser.stream.current
        lineno = next (parser.stream).lineno
        cond   = parser.parse_expression ()
        ### first, seek to the start of the "head" token
        parser.parse_statements (["name:head"], drop_needle = True)
        h_then = parser.parse_statements (["name:else", "name:body"])
        if parser.stream.current.value == "else" :
            next (parser.stream)
            h_else = parser.parse_statements (["name:body"])
        else :
            h_else = None
        next (parser.stream)
        body   = parser.parse_statements (["name:endonion", "name:tail"])
        result = [nodes.If ( cond, h_then, h_else)]
        result.extend (body)
        if parser.stream.current.value == "tail" :
            next (parser.stream)
            t_then = parser.parse_statements (["name:else", "name:endonion"])
            if parser.stream.current.value == "else" :
                next (parser.stream)
                t_else = parser.parse_statements (["name:endonion"])
            else :
                t_else = None
            result.append (nodes.If (cond, t_then, t_else))
        next (parser.stream)
        return result
    # end def parse

# end class Onion

if __name__ != "__main__" :
    JNJ._Export ("Onion")
### __END__ JNJ.Onion
