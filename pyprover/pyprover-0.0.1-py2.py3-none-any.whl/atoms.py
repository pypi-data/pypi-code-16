#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x4b2cf565

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

from contextlib import contextmanager

from pyprover.tools import propositions
from pyprover.tools import variables

# Base Class:

class Vars(_coconut.object):
    @classmethod
    def items(cls):
        for name, var in vars(cls).items():
            if not name.startswith("_"):
                yield name, var
    @classmethod
    def use(cls, globs=None):
        """Put variables into the global namespace."""
        if globs is None:
            globs = globals()
        for name, var in cls.items():
            globs[name] = var
    @classmethod
    @contextmanager
    def using(cls, globs=None):
        """Temporarilty put variables into the global namespace."""
        if globs is None:
            globs = globals()
        prevars = {}
        for name, var in cls.items():
            if name in globs:
                prevars[name] = globs[name]
            globs[name] = var
        try:
            yield
        finally:
            for name, var in cls.items():
                if name in prevars:
                    globs[name] = prevars[name]
                else:
                    del globs[name]

# Derived Classes:

class LowercasePropositions(Vars):
    a, b, c = propositions("a b c")
    d, e, f = propositions("d e f")
    g, h, i = propositions("g h i")
    j, k, l = propositions("j k l")
    m, n, o = propositions("m n o")
    p, q, r = propositions("p q r")
    s, t, u = propositions("s t u")
    v, w, x = propositions("v w x")
    y, z = propositions("y z")

class UppercasePropositions(Vars):
    B, C = propositions("B C")
    D, F = propositions("D F")
    G, H, I = propositions("G H I")
    J, K, L = propositions("J K L")
    M, N, O = propositions("M N O")
    P, Q, R = propositions("P Q R")
    S, T, U = propositions("S T U")
    V, W, X = propositions("V W X")
    Y, Z = propositions("Y Z")

class LowercaseVariables(Vars):
    a, b, c = variables("a b c")
    d, e, f = variables("d e f")
    g, h, i = variables("g h i")
    j, k, l = variables("j k l")
    m, n, o = variables("m n o")
    p, q, r = variables("p q r")
    s, t, u = variables("s t u")
    v, w, x = variables("v w x")
    y, z = variables("y z")

class UppercaseVariables(Vars):
    B, C = variables("B C")
    D, F = variables("D F")
    G, H, I = variables("G H I")
    J, K, L = variables("J K L")
    M, N, O = variables("M N O")
    P, Q, R = variables("P Q R")
    S, T, U = variables("S T U")
    V, W, X = variables("V W X")
    Y, Z = variables("Y Z")

class StandardMath(Vars): pass
for name, var in _coconut.itertools.chain.from_iterable((_coconut_lazy_item() for _coconut_lazy_item in (lambda: LowercaseVariables.items(), lambda: UppercasePropositions.items()))):
    setattr(StandardMath, name, var)
