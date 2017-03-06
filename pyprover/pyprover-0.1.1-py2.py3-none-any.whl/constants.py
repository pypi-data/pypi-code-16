#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x3183ad0f

# Compiled with Coconut version 1.2.2-post_dev4 [Colonel]

# Coconut Header: --------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_tee, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: ------------------------------------------------------

# Imports:

import sys  # line 3

# Utilities:

def first_encodeable(*symbols):  # line 7
    for sym in symbols:  # line 8
        try:  # line 9
            sym.encode(sys.stdout.encoding)  # line 10
        except UnicodeEncodeError:  # line 11
            pass  # line 12
        else:  # line 13
            return sym  # line 14
    raise ValueError("No encodeable symbol in " + repr(symbols))  # line 15

# Installation:

version = "0.1.1"  # line 19
requirements = []  # line 20
classifiers = ["Development Status :: 3 - Alpha", "License :: OSI Approved :: Apache Software License", "Topic :: Software Development :: Libraries :: Python Modules", "Topic :: Utilities", "Operating System :: OS Independent",]  # line 21

# Symbols:

top_sym = first_encodeable("\u22a4", "\u252c", "-T-")  # line 31
bot_sym = first_encodeable("\u22a5", "\u2534", "_|_")  # line 32
not_sym = first_encodeable("\xac", "~")  # line 33
imp_sym = first_encodeable("\u2192", "->")  # line 34
and_sym = first_encodeable("\u2227", "/\\")  # line 35
or_sym = first_encodeable("\u2228", "\\/")  # line 36
forall_sym = first_encodeable("\u2200", "A:")  # line 37
exists_sym = first_encodeable("\u2203", "E:")  # line 38
