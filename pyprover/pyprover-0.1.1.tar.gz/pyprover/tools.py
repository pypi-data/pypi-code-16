#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xd2f04006

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

from pyprover.logic import Proposition  # line 2
from pyprover.logic import Constant  # line 2
from pyprover.logic import And  # line 2
from pyprover.logic import wff  # line 2
from pyprover.logic import bot  # line 3

# Functions:

@_coconut_tco  # line 12
def propositions(names):  # line 12
    """Constructs propositions from a space-seperated string of names."""  # line 14
    raise _coconut_tail_call(map, Proposition, names.split())  # line 15

@_coconut_tco  # line 16
def terms(names):  # line 16
    """Constructs constants from a space-seperated string of names."""  # line 18
    raise _coconut_tail_call(map, Constant, names.split())  # line 19

def solve(expr, **kwargs):  # line 20
    """Converts to CNF and performs all possible resolutions."""  # line 22
    return expr.simplify(dnf=False, **kwargs).resolve(**kwargs)  # line 23

def proves(givens, conclusion, **kwargs):  # line 24
    """Determines if the givens prove the conclusion."""  # line 26
    if wff(givens):  # line 27
        givens = (givens,)  # line 28
    else:  # line 29
        givens = tuple(givens)  # line 30
        assert all((wff(x) for x in givens))  # line 31
    ands = givens + (~conclusion,)  # line 32
    return (_coconut.functools.partial(solve, **kwargs))(And(*ands)) == bot  # line 33

def iff(a, b, **kwargs):  # line 34
    """Determines if a is true if and only if b."""  # line 36
    a = a.simplify(dnf=False, **kwargs)  # line 37
    b = b.simplify(dnf=False, **kwargs)  # line 38
    return (_coconut.functools.partial(proves, **kwargs))(a, b) and (_coconut.functools.partial(proves, **kwargs))(b, a)  # line 39

@_coconut_tco  # line 40
def simplify(expr, *exprs, **kwargs):  # line 41
    """Simplify the given expression[s]."""  # line 42
    if exprs:  # line 43
        raise _coconut_tail_call((tuple), (_coconut.functools.partial(map, lambda x: x.simplify(**kwargs)))((expr,) + exprs))  # line 44
    else:  # line 45
        raise _coconut_tail_call(expr.simplify, **kwargs)  # line 46

def simplest_form(expr, **kwargs):  # line 48
    """Finds the shortest simplification for the given expression."""  # line 49
    cnf_expr = expr.simplify(dnf=False, **kwargs)  # line 50
    dnf_expr = cnf_expr.simplify(dnf=True, **kwargs)  # line 51
    if len(cnf_expr) <= len(dnf_expr):  # line 52
        return cnf_expr  # line 53
    else:  # line 54
        return dnf_expr  # line 55

@_coconut_tco  # line 56
def simplest_solution(expr, **kwargs):  # line 56
    """Finds the shortest resolved simplification for the given expression."""  # line 58
    raise _coconut_tail_call((_coconut.functools.partial(simplest_form, **kwargs)), (_coconut.functools.partial(solve, **kwargs))(expr))  # line 59

@_coconut_tco  # line 60
def sub_in(expr, subs):  # line 60
    """Substitutes expressions or booleans into the given expression."""  # line 62
    raise _coconut_tail_call(expr.substitute, subs)  # line 63
