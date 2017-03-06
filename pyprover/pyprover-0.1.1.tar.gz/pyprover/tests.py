#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x7c410b3

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

from pyprover.logic import FA  # line 2
from pyprover.logic import TE  # line 2
from pyprover.logic import top  # line 2
from pyprover.logic import bot  # line 2
from pyprover.logic import And  # line 2
from pyprover.logic import Or  # line 3
from pyprover.tools import proves  # line 4
from pyprover.tools import iff  # line 4
from pyprover.tools import simplify  # line 4
from pyprover.tools import simplest_form  # line 4
from pyprover.tools import sub_in  # line 11
from pyprover.atoms import LowercasePropositions  # line 12
from pyprover.atoms import StandardMath  # line 18

# Tests:

def test_propositional_logic():  # line 25
    """Runs propositional logic tests."""  # line 26
    with LowercasePropositions.using(globals()) :  # line 27

# constructive theorems
        assert (proves)(e & f, e)  # line 30
        assert (proves)(e & f, f)  # line 31
        assert (proves)((e >> f, f >> g, e), g)  # line 32
        assert (proves)((e >> (f >> g), e >> f, e), g)  # line 33
        assert (proves)((e >> f, f >> g), e >> g)  # line 34
        assert (proves)(e >> (f >> g), f >> (e >> g))  # line 35
        assert (proves)(e >> (f >> g), (e >> f) >> (e >> g))  # line 36
        assert (proves)(e, f >> e)  # line 37
        assert (proves)(top, e >> (f >> e))  # line 38
        assert (proves)(e >> (f & g), (e >> f) & (e >> g))  # line 39
        assert (proves)(e >> (f >> g), (e & f) >> g)  # line 40
        assert (proves)((e & f) >> g, e >> (f >> g))  # line 41
        assert (proves)((e >> f) >> g, (e & f) >> g)  # line 42
        assert (proves)(e & (f >> g), (e >> f) >> g)  # line 43
        assert (proves)(e, e | f)  # line 44
        assert (proves)(f, e | f)  # line 45
        assert (proves)(e | f, f | e)  # line 46
        assert (proves)(f >> g, (e | f) >> (e | g))  # line 47
        assert (proves)(e, e | e)  # line 48
        assert (proves)(e, ~~e)  # line 49
        assert (proves)(~e, e >> f)  # line 50
        assert (proves)(e >> f, ~f >> ~e)  # line 51
        assert (proves)(e | f, ~(~e & ~f))  # line 52
        assert (proves)(e & f, ~(~e | ~f))  # line 53
        assert (proves)(~(e | f), ~e & ~f)  # line 54
        assert (proves)(~e & ~f, ~(e | f))  # line 55
        assert (proves)(~e | ~f, ~(e & f))  # line 56
        assert (proves)(top, ~(e & ~e))  # line 57
        assert (proves)(e & ~e, f)  # line 58
        assert (proves)(~f, f >> g)  # line 59
        assert (proves)((f >> g, ~f >> g), g)  # line 60
        assert (proves)(g, f >> g)  # line 61
        assert (proves)((f, ~(f & g)), ~g)  # line 62
        assert (proves)((p >> r, p >> ~r), ~p)  # line 63
        assert (proves)(top, (p >> ~p) >> ~p)  # line 64
        assert (proves)(bot, a)  # line 65
        assert (proves)(bot, top)  # line 66
        assert (proves)(a, top)  # line 67

# classical theorems
        assert (proves)(~~e, e)  # line 70
        assert (proves)(top, e | ~e)  # line 71
        assert (proves)(top, ((e >> f) >> e) >> e)  # line 72
        assert (proves)(~f >> ~e, e >> f)  # line 73
        assert (proves)(~(~e & ~f), e | f)  # line 74
        assert (proves)(~(~e | ~f), e & f)  # line 75
        assert (proves)(~(e & f), ~e | ~f)  # line 76
        assert (proves)(top, (e >> f) | (f >> e))  # line 77
        assert (proves)(top, (~~a | a) >> a)  # line 78
        assert (proves)(p >> r, (f >> r) | (p >> g))  # line 79
        assert (proves)(~(f >> g), f & ~g)  # line 80
        assert (proves)(top, (~f >> bot) >> f)  # line 81
        assert (proves)(f >> g, ~f | g)  # line 82
        assert (proves)(top, r & s | (~r | ~s))  # line 83
        assert (proves)(f >> g, g | ~f)  # line 84
        assert (proves)((a & b) >> ~c, ~a | ~b | ~c)  # line 85
        assert (proves)(f >> (g >> h), ~f | ~g | h)  # line 86

# other theorems
        assert (proves)(t & (t >> d) | ~t & ~(t >> d), d)  # line 89
        assert (proves)((f >> g, c >> d), (f | c) >> (g | d))  # line 90
        assert (proves)((f >> g) >> h, f >> (g >> h))  # line 91
        assert (proves)(top, p >> (s >> p))  # line 92
        assert (proves)(~f | (f >> g), ~f | g)  # line 93
        assert (proves)((~f, g >> f), ~g)  # line 94
        assert (proves)((p >> s, r >> t, ~s | ~t), ~p | ~r)  # line 95
        assert (proves)(top, ~~(f | ~f))  # line 96
        assert (proves)(top, ~~(~~f >> f))  # line 97
        assert (proves)((p | r, ~p), r)  # line 98
        assert (proves)((f | g, ~f), g)  # line 99
        assert (proves)((t | ~a, ~a | ~t), ~a)  # line 100
        assert (proves)(top, ~~((~f >> bot) >> f))  # line 101
        assert (proves)((s & h | ~s & ~h) & ~(s & h) | (s & ~h | ~s & h) & (s & h), ~s & ~h)  # line 102
        assert (proves)(~a | ~b | ~c, (a & b) >> ~c)  # line 103
        assert (proves)(~p, p >> bot)  # line 104
        assert (proves)((a | b, ~a | c), b | c)  # line 105
        assert (proves)(top, (f & g) >> g)  # line 106
        assert (proves)((p >> s, r >> t, p | r), s | t)  # line 107
        assert (proves)(top, ~p >> (p >> s))  # line 108
        assert (proves)(f >> g, ((f & g) >> f) | (f >> (f & g)))  # line 109
        assert (proves)((f | ~f) >> g, ~~g)  # line 110
        assert (proves)(p >> r, p >> (p & r))  # line 111
        assert (proves)((s & h | ~s & ~h) & (h | s) | (s & ~h | ~s & h) & ~(h | s), s & h)  # line 112
        assert (proves)(~(f >> g), g >> f)  # line 113
        assert (proves)((f >> g) & (f >> h), f >> (g & h))  # line 114
        assert (proves)((s & h | ~s & ~h) & (~s & ~h) | (s & ~h | ~s & h) & ~(~s & ~h), ~(s & h))  # line 115
        assert (proves)(top, (p >> (s >> e)) >> ((p >> s) >> (p >> e)))  # line 116
        assert (proves)(top, p >> p)  # line 117
        assert (proves)(~f, ~(f & g))  # line 118
        assert (proves)(f >> ~f, ~f)  # line 119
        assert (proves)(f >> g, ~g >> ~f)  # line 120
        assert (f & g) >> f  # line 121
        assert (proves)((f >> (t & a | ~t & ~a), t & ~f | ~t & f, g >> (t & ~a | ~t & a), t & g | ~t & ~g), ~a)  # line 122
        assert (proves)(t & (~t & ~a) | ~t & ~(~t & ~a), a)  # line 123
        assert (proves)(~f | ~g | h, f >> (g >> h))  # line 124

# invalid theorems
        assert not (proves)(e >> (f >> g), (e >> f) >> g)  # line 127
        assert not (proves)((e & f) >> g, (e >> f) >> g)  # line 128
        assert not (proves)((e >> f) >> g, e & (f >> g))  # line 129
        assert not (proves)(e, e & f)  # line 130
        assert not (proves)(e | f, e & f)  # line 131
        assert not (proves)(e | top, e)  # line 132
        assert not (proves)(e, e & bot)  # line 133
        assert not (proves)(top, bot)  # line 134

# other tests
        assert And() == top  # line 137
        assert Or() == bot  # line 138
        assert (proves)((a ^ b, a), ~b)  # line 139
        assert (iff)(f >> (g >> h), (f & g) >> h)  # line 140
        assert (iff)(bot, a & ~a)  # line 141
        assert (iff)(top, a | ~a)  # line 142
        assert (simplify)(top & bot) == bot  # line 143
        assert simplify(a & a, b & b) == (a, b)  # line 144
        assert (simplest_form)(a ^ b) == (b | a) & (~a | ~b)  # line 145
        assert (simplest_form)((s & h | ~s & ~h) & ~(s & h) | (s & ~h | ~s & h) & (s & h)) == ~s & ~h  # line 146
        assert (simplify)((sub_in)(a ^ b, {a: True, b: False})) == top  # line 147
        assert (simplify)((sub_in)(a ^ b, {a: top, b: top})) == bot  # line 148

def test_predicate_logic():  # line 150
    """Runs predicate logic tests."""  # line 151
    with StandardMath.using(globals()) :  # line 152

# basic tests
        assert (simplify)(FA(x, F)) == F  # line 155
        assert (simplify)(TE(x, F)) == F  # line 156
        assert (simplify)(FA(x, F(x)) & G(x)) == FA(y, F(y) & G(x))  # line 157
        assert (simplify)(FA(x, F(x)) | G(x)) == FA(y, F(y) | G(x))  # line 158
        assert (simplify)(TE(x, F(x)) & G(x)) == TE(y, F(y) & G(x))  # line 159
        assert (simplify)(TE(x, F(x)) | G(x)) == TE(y, F(y) | G(x))  # line 160
        assert FA(x, F(f(x))) == FA(y, F(f(y)))  # line 161
        assert TE(x, F(f(x))) == TE(y, F(f(y)))  # line 162
        assert TE(f, F(f(x))) == TE(g, F(g(x)))  # line 163

# constructive theorems
        assert (proves)(TE(x, bot), bot)  # line 166
        assert (proves)(top, FA(x, top))  # line 167
        assert (proves)(FA(x, R(x) >> S(x)), FA(y, R(y)) >> FA(z, S(z)))  # line 168
        assert (proves)(FA(x, R(x) & S(x)), FA(y, R(y)) & FA(z, S(z)))  # line 169
        assert (proves)((FA(x, R(x) >> S(x)), TE(y, R(y))), TE(z, S(z)))  # line 170
        assert (proves)(TE(x, R(x) & S(x)), TE(y, R(y)) & TE(z, S(z)))  # line 171
        assert (proves)(TE(x, R(x)) | TE(y, S(y)), TE(z, R(z) | S(z)))  # line 172
        assert (proves)(TE(x, R(x) | S(x)), TE(y, R(y)) | TE(z, S(z)))  # line 173
        assert (proves)(FA(x, R(x)), ~TE(y, ~R(y)))  # line 174
        assert (proves)(TE(x, ~R(x)), ~FA(y, R(y)))  # line 175
        assert (proves)(FA(x, ~R(x)), ~TE(y, R(y)))  # line 176
        assert (proves)(~TE(x, R(x)), FA(y, ~R(y)))  # line 177
        assert (proves)(R(j), TE(x, R(x)))  # line 178

# classical theorems
        assert (proves)(~TE(x, ~R(x)), FA(y, R(y)))  # line 181
        assert (proves)(~FA(x, ~R(x)), TE(y, R(y)))  # line 182
        assert (proves)(~FA(x, R(x)), TE(y, ~R(y)))  # line 183
        assert (proves)(FA(x, ~~D(x)), FA(x, D(x)))  # line 184
        assert (proves)(~TE(x, R(x)), FA(y, ~R(y)))  # line 185
        assert (proves)(top, TE(x, D(x)) | FA(x, ~D(x)))  # line 186
        assert (proves)(top, TE(x, ~D(x)) | FA(x, D(x)))  # line 187
        assert (proves)(TE(x, top), TE(x, D(x) >> FA(y, D(y))))  # line 188
        assert (proves)(TE(x, ~~D(x)), TE(x, D(x)))  # line 189
        assert (proves)(FA(x, C(x) | D(x)), FA(x, C(x)) | TE(x, D(x)))  # line 190

# other theorems
        assert (proves)(FA(x, H(j) >> T(x)), H(j) >> FA(x, T(x)))  # line 193
        assert (proves)(TE(x, R(x) >> B(x)), FA(x, R(x)) >> TE(x, B(x)))  # line 194
        assert (proves)(~FA(x, bot), TE(x, top))  # line 195
        assert (proves)(FA(x, TE(y, F(y) | G(x))), FA(x, G(x) | TE(x, F(x))))  # line 196
        assert (proves)((FA(x, FA(y, FA(z, (S(x, y) & S(y, z)) >> S(x, z)))), ~TE(x, S(x, x))), FA(x, FA(y, S(x, y) >> ~S(y, x))))  # line 197
        assert (proves)(FA(x, G(x)) | FA(x, B(x)), FA(x, G(x) | B(x)))  # line 198
        assert (proves)(TE(z, FA(k, P(z, k))), FA(y, TE(x, P(x, y))))  # line 199
        assert (proves)(TE(x, C(x) & B(x)), TE(x, B(x) & C(x)))  # line 200
        assert (proves)(TE(x, C(x, i) & B(x, j)), TE(x, C(x, i) >> B(x, j)))  # line 201
        assert (proves)(FA(x, C(x) & B(x)), FA(x, B(x) & C(x)))  # line 202
        assert (proves)(FA(x, C(x) & B(x)), FA(x, C(x)) & FA(x, B(x)))  # line 203
        assert (proves)(FA(x, bot), ~TE(x, top))  # line 204
        assert (proves)((~TE(x, G(x)) | FA(x, F(x)), C(j) >> FA(x, D(x))), FA(y, FA(z, ~G(z) | F(y) & C(j) >> D(y))))  # line 205
        assert (proves)(FA(x, G(x)) | TE(x, F(x)), FA(x, TE(y, F(y) | G(x))))  # line 206
        assert (proves)((P | TE(x, W)) >> FA(z, R), FA(z, FA(x, (P | W) >> R)))  # line 207

# invalid theorems
        assert not (proves)(FA(x, R(x)) >> FA(y, S(y)), FA(z, R(z) >> S(z)))  # line 210
        assert not (proves)(TE(x, R(x)) & TE(y, S(y)), TE(z, R(z) & S(z)))  # line 211
        assert not (proves)(TE(x, R(x)), FA(y, R(y)))  # line 212

# non-empty universe theorems
        assert (proves)(top, TE(x, top))  # line 215
        assert (proves)(top, TE(x, D(x) >> FA(y, D(y))))  # line 216
        assert (proves)((R(j), FA(x, R(x) >> S(x))), S(j))  # line 217
        assert (proves)(FA(x, R(x)) >> FA(y, S(y)), TE(x, FA(y, ~R(x) | S(y))))  # line 218
        assert (proves)(FA(x, R(x)), TE(y, R(y)))  # line 219
        assert (proves)(TE(x, ~R(x)), TE(y, R(y) >> (R(j) & R(k))))  # line 220
        assert (proves)((T(i), FA(x, T(x) >> T(s(x)))), T(s(i)))  # line 221
        assert (proves)(top, TE(x, R(x) >> (R(j) & R(k))))  # line 222

if __name__ == "__main__":  # line 224
    test_propositional_logic()  # line 225
    test_predicate_logic()  # line 226
    print("<success>")  # line 227
