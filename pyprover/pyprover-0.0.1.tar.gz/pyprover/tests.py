#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x8bb5e84c

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

from pyprover.logic import A
from pyprover.logic import E
from pyprover.tools import proves
from pyprover.tools import iff
from pyprover.tools import simplify
from pyprover.tools import simplest_form
from pyprover.tools import sub_in
from pyprover.atoms import LowercasePropositions
from pyprover.atoms import StandardMath

# Tests:

def test_propositional_logic():
    """Runs propositional logic tests."""
    with LowercasePropositions.using(globals()) :

# constructive theorems
        assert (proves)(e & f, e)
        assert (proves)(e & f, f)
        assert (proves)((e >> f, f >> g, e), g)
        assert (proves)((e >> (f >> g), e >> f, e), g)
        assert (proves)((e >> f, f >> g), e >> g)
        assert (proves)(e >> (f >> g), f >> (e >> g))
        assert (proves)(e >> (f >> g), (e >> f) >> (e >> g))
        assert (proves)(e, f >> e)
        assert (proves)(top, e >> (f >> e))
        assert (proves)(e >> (f & g), (e >> f) & (e >> g))
        assert (proves)(e >> (f >> g), (e & f) >> g)
        assert (proves)((e & f) >> g, e >> (f >> g))
        assert (proves)((e >> f) >> g, (e & f) >> g)
        assert (proves)(e & (f >> g), (e >> f) >> g)
        assert (proves)(e, e | f)
        assert (proves)(f, e | f)
        assert (proves)(e | f, f | e)
        assert (proves)(f >> g, (e | f) >> (e | g))
        assert (proves)(e, e | e)
        assert (proves)(e, ~~e)
        assert (proves)(~e, e >> f)
        assert (proves)(e >> f, ~f >> ~e)
        assert (proves)(e | f, ~(~e & ~f))
        assert (proves)(e & f, ~(~e | ~f))
        assert (proves)(~(e | f), ~e & ~f)
        assert (proves)(~e & ~f, ~(e | f))
        assert (proves)(~e | ~f, ~(e & f))
        assert (proves)(top, ~(e & ~e))
        assert (proves)(e & ~e, f)
        assert (proves)(~f, f >> g)
        assert (proves)((f >> g, ~f >> g), g)
        assert (proves)(g, f >> g)
        assert (proves)((f, ~(f & g)), ~g)
        assert (proves)((p >> r, p >> ~r), ~p)
        assert (proves)(top, (p >> ~p) >> ~p)
        assert (proves)(bot, a)
        assert (proves)(bot, top)
        assert (proves)(a, top)

# classical theorems
        assert (proves)(~~e, e)
        assert (proves)(top, e | ~e)
        assert (proves)(top, ((e >> f) >> e) >> e)
        assert (proves)(~f >> ~e, e >> f)
        assert (proves)(~(~e & ~f), e | f)
        assert (proves)(~(~e | ~f), e & f)
        assert (proves)(~(e & f), ~e | ~f)
        assert (proves)(top, (e >> f) | (f >> e))
        assert (proves)(top, (~~a | a) >> a)
        assert (proves)(p >> r, (f >> r) | (p >> g))
        assert (proves)(~(f >> g), f & ~g)
        assert (proves)(top, (~f >> bot) >> f)
        assert (proves)(f >> g, ~f | g)
        assert (proves)(top, r & s | (~r | ~s))
        assert (proves)(f >> g, g | ~f)
        assert (proves)((a & b) >> ~c, ~a | ~b | ~c)
        assert (proves)(f >> (g >> h), ~f | ~g | h)

# other theorems
        assert (proves)(t & (t >> d) | ~t & ~(t >> d), d)
        assert (proves)((f >> g, c >> d), (f | c) >> (g | d))
        assert (proves)((f >> g) >> h, f >> (g >> h))
        assert (proves)(top, p >> (s >> p))
        assert (proves)(~f | (f >> g), ~f | g)
        assert (proves)((~f, g >> f), ~g)
        assert (proves)((p >> s, r >> t, ~s | ~t), ~p | ~r)
        assert (proves)(top, ~~(f | ~f))
        assert (proves)(top, ~~(~~f >> f))
        assert (proves)((p | r, ~p), r)
        assert (proves)((f | g, ~f), g)
        assert (proves)((t | ~a, ~a | ~t), ~a)
        assert (proves)(top, ~~((~f >> bot) >> f))
        assert (proves)((s & h | ~s & ~h) & ~(s & h) | (s & ~h | ~s & h) & (s & h), ~s & ~h)
        assert (proves)(~a | ~b | ~c, (a & b) >> ~c)
        assert (proves)(~p, p >> bot)
        assert (proves)((a | b, ~a | c), b | c)
        assert (proves)(top, (f & g) >> g)
        assert (proves)((p >> s, r >> t, p | r), s | t)
        assert (proves)(top, ~p >> (p >> s))
        assert (proves)(f >> g, ((f & g) >> f) | (f >> (f & g)))
        assert (proves)((f | ~f) >> g, ~~g)
        assert (proves)(p >> r, p >> (p & r))
        assert (proves)((s & h | ~s & ~h) & (h | s) | (s & ~h | ~s & h) & ~(h | s), s & h)
        assert (proves)(~(f >> g), g >> f)
        assert (proves)((f >> g) & (f >> h), f >> (g & h))
        assert (proves)((s & h | ~s & ~h) & (~s & ~h) | (s & ~h | ~s & h) & ~(~s & ~h), ~(s & h))
        assert (proves)(top, (p >> (s >> e)) >> ((p >> s) >> (p >> e)))
        assert (proves)(top, p >> p)
        assert (proves)(~f, ~(f & g))
        assert (proves)(f >> ~f, ~f)
        assert (proves)(f >> g, ~g >> ~f)
        assert (f & g) >> f
        assert (proves)((f >> (t & a | ~t & ~a), t & ~f | ~t & f, g >> (t & ~a | ~t & a), t & g | ~t & ~g), ~a)
        assert (proves)(t & (~t & ~a) | ~t & ~(~t & ~a), a)
        assert (proves)(~f | ~g | h, f >> (g >> h))

# invalid theorems
        assert not (proves)(e >> (f >> g), (e >> f) >> g)
        assert not (proves)((e & f) >> g, (e >> f) >> g)
        assert not (proves)((e >> f) >> g, e & (f >> g))
        assert not (proves)(e, e & f)
        assert not (proves)(e | f, e & f)
        assert not (proves)(e | top, e)
        assert not (proves)(e, e & bot)
        assert not (proves)(top, bot)

# other tests
        assert And() == top
        assert Or() == bot
        assert (proves)((a ^ b, a), ~b)
        assert (iff)(f >> (g >> h), (f & g) >> h)
        assert (iff)(bot, a & ~a)
        assert (iff)(top, a | ~a)
        assert (simplify)(top & bot) == bot
        assert simplify(a & a, b & b) == (a, b)
        assert (simplest_form)(a ^ b) == (b | a) & (~a | ~b)
        assert (simplest_form)((s & h | ~s & ~h) & ~(s & h) | (s & ~h | ~s & h) & (s & h)) == ~s & ~h
        assert (simplify)((sub_in)(a ^ b, {a: True, b: False})) == top
        assert (simplify)((sub_in)(a ^ b, {a: top, b: top})) == bot

def test_predicate_logic():
    """Runs predicate logic tests."""
    with StandardMath.using(globals()) :

# basic tests
        assert (simplify)(A(x, F)) == F
        assert (simplify)(E(x, F)) == F
        assert (simplify)(A(x, F(x)) & G(x)) == A(y, F(y) & G(x))
        assert (simplify)(A(x, F(x)) | G(x)) == A(y, F(y) | G(x))
        assert (simplify)(E(x, F(x)) & G(x)) == E(y, F(y) & G(x))
        assert (simplify)(E(x, F(x)) | G(x)) == E(y, F(y) | G(x))
        assert A(x, F(f(x))) == A(y, F(f(y)))
        assert E(x, F(f(x))) == E(y, F(f(y)))
        assert E(f, F(f(x))) == E(g, F(g(x)))

# constructive theorems
        assert (proves)(E(x, bot), bot)
        assert (proves)(top, A(x, top))
        assert (proves)(A(x, R(x) >> S(x)), A(y, R(y)) >> A(z, S(z)))
        assert (proves)(A(x, R(x) & S(x)), A(y, R(y)) & A(z, S(z)))
        assert (proves)((A(x, R(x) >> S(x)), E(y, R(y))), E(z, S(z)))
        assert (proves)(E(x, R(x) & S(x)), E(y, R(y)) & E(z, S(z)))
        assert (proves)(E(x, R(x)) | E(y, S(y)), E(z, R(z) | S(z)))
        assert (proves)(E(x, R(x) | S(x)), E(y, R(y)) | E(z, S(z)))
        assert (proves)(A(x, R(x)), ~E(y, ~R(y)))
        assert (proves)(E(x, ~R(x)), ~A(y, R(y)))
        assert (proves)(A(x, ~R(x)), ~E(y, R(y)))
        assert (proves)(~E(x, R(x)), A(y, ~R(y)))
        assert (proves)(R(j), E(x, R(x)))

# classical theorems
        assert (proves)(~E(x, ~R(x)), A(y, R(y)))
        assert (proves)(~A(x, ~R(x)), E(y, R(y)))
        assert (proves)(~A(x, R(x)), E(y, ~R(y)))
        assert (proves)(A(x, ~~D(x)), A(x, D(x)))
        assert (proves)(~E(x, R(x)), A(y, ~R(y)))
        assert (proves)(top, E(x, D(x)) | A(x, ~D(x)))
        assert (proves)(top, E(x, ~D(x)) | A(x, D(x)))
        assert (proves)(E(x, top), E(x, D(x) >> A(y, D(y))))
        assert (proves)(E(x, ~~D(x)), E(x, D(x)))
        assert (proves)(A(x, C(x) | D(x)), A(x, C(x)) | E(x, D(x)))

# other theorems
        assert (proves)(A(x, H(j) >> T(x)), H(j) >> A(x, T(x)))
        assert (proves)(E(x, R(x) >> B(x)), A(x, R(x)) >> E(x, B(x)))
        assert (proves)(~A(x, bot), E(x, top))
        assert (proves)(A(x, E(y, F(y) | G(x))), A(x, G(x) | E(x, F(x))))
        assert (proves)((A(x, A(y, A(z, S(x, y) & S(y, z) >> S(x, z)))), ~E(x, S(x, x))), A(x, A(y, S(x, y) >> ~S(y, x))))
        assert (proves)(A(x, G(x)) | A(x, B(x)), A(x, G(x) | B(x)))
        assert (proves)(E(z, A(k, P(z, k))), A(y, E(x, P(x, y))))
        assert (proves)(E(x, C(x) & B(x)), E(x, B(x) & C(x)))
        assert (proves)(E(x, C(x, i) & B(x, j)), E(x, C(x, i) >> B(x, j)))
        assert (proves)(A(x, C(x) & B(x)), A(x, B(x) & C(x)))
        assert (proves)(A(x, C(x) & B(x)), A(x, C(x)) & A(x, B(x)))
        assert (proves)(A(x, bot), ~E(x, top))
        assert (proves)((~E(x, G(x)) | A(x, F(x)), C(j) >> A(x, D(x))), A(y, A(z, ~G(z) | F(y) & C(j) >> D(y))))
        assert (proves)(A(x, G(x)) | E(x, F(x)), A(x, E(y, F(y) | G(x))))
        assert (proves)((P | E(x, W)) >> A(z, R), A(z, A(x, (P | W) >> R)))

# invalid theorems
        assert not (proves)(A(x, R(x)) >> A(y, S(y)), A(z, R(z) >> S(z)))
        assert not (proves)(E(x, R(x)) & E(y, S(y)), E(z, R(z) & S(z)))
        assert not (proves)(E(x, R(x)), A(y, R(y)))

# non-empty universe theorems
        assert (proves)(top, E(x, top))
        assert (proves)(top, E(x, D(x) >> A(y, D(y))))
        assert (proves)((R(j), A(x, R(x) >> S(x))), S(j))
        assert (proves)(A(x, R(x)) >> A(y, S(y)), E(x, A(y, ~R(x) | S(y))))
        assert (proves)(A(x, R(x)), E(y, R(y)))
        assert (proves)(E(x, ~R(x)), E(y, R(y) >> (R(j) & R(k))))
        assert (proves)((T(i), A(x, T(x) >> T(s(x)))), T(s(i)))
        assert (proves)(top, E(x, R(x) >> (R(j) & R(k))))

if __name__ == "__main__":
    test_propositional_logic
    test_predicate_logic
