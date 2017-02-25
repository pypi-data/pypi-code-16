# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Mag. Christian Tanzer All rights reserved
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
#    TFL.r_eval
#
# Purpose
#    Restricted `eval`
#
# Revision Dates
#     7-Jun-2012 (CT) Creation
#     8-Jun-2012 (CT) Add `\s*` to `_eval_restrict_pat`
#     6-Jun-2013 (CT) Change guard to `isinstance (source, pyk.string_types)`
#     4-Dec-2013 (CT) Remove `coding` cookie from unicode values
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function

from   _TFL        import TFL
from   _TFL.pyk    import pyk

import re

_coding_pat        = re.compile \
    ( r"^# *(-\*-)?\s*coding[:=]\s*[-a-zA-Z0-9]+ *(-\*-)? *" + "\n"
    , re.MULTILINE
    )

_eval_restrict_pat = re.compile \
    ( r"(?: (?: ^|\W)(?: lambda)(?: \W|$))|\.\s*__|(?: ^|\W)inspect\."
    , re.VERBOSE
    )

def r_eval (source, ** kw) :
    """Evaluate `source`, in a scope with values of `kw`, but nothing else.


    >>> r_eval ("2 * 2")
    4
    >>> r_eval ("dir ()")
    Traceback (most recent call last):
    ...
    NameError: name 'dir' is not defined
    >>> r_eval ("dir ()", dir = dir)
    ['__builtins__', 'dir']
    >>> r_eval ("type (())")
    Traceback (most recent call last):
    ...
    NameError: name 'type' is not defined
    >>> r_eval ("lambda : 5")
    Traceback (most recent call last):
    ...
    ValueError: Cannot safely evaluate 'lambda : 5'
    >>> r_eval ("().__class__")
    Traceback (most recent call last):
    ...
    ValueError: Cannot safely evaluate '().__class__'
    >>> r_eval ("((). __class__)")
    Traceback (most recent call last):
    ValueError: Cannot safely evaluate '((). __class__)'
    """
    if isinstance (source, pyk.text_type) :
        source = _coding_pat.sub ("", source, 1)
    if isinstance (source, pyk.string_types) :
        if _eval_restrict_pat.search (source) :
            raise ValueError ("Cannot safely evaluate %r" % source)
        scope = dict (kw, __builtins__ = {})
        return eval (source, scope)
# end def r_eval

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.r_eval
