#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xf2ba398

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

from pyprover.constants import top_sym  # line 2
from pyprover.constants import bot_sym  # line 2
from pyprover.constants import not_sym  # line 2
from pyprover.constants import imp_sym  # line 2
from pyprover.constants import and_sym  # line 2
from pyprover.constants import or_sym  # line 2
from pyprover.constants import forall_sym  # line 2
from pyprover.constants import exists_sym  # line 3
from pyprover.util import unorderd_eq  # line 4
from pyprover.util import quote  # line 13

# Functions:

def wff(expr):  # line 19
    """Determines whether expr is a well-formed formula."""  # line 21
    return isinstance(expr, Expr) and not isinstance(expr, Term)  # line 22

@_coconut_tco  # line 23
def isvar(var):  # line 23
    """Whether a term is a variable."""  # line 25
    raise _coconut_tail_call(isinstance, var, (Constant, Variable))  # line 26

# Classes:

class Expr(_coconut.object):  # line 30
    __slots__ = ()  # line 31
    @_coconut_tco  # line 32
    def __and__(self, other):  # line 32
        if isinstance(other, And):  # line 33
            return other & self  # line 34
        else:  # line 35
            raise _coconut_tail_call(And, self, other)  # line 36
    @_coconut_tco  # line 37
    def __or__(self, other):  # line 37
        if isinstance(other, Or):  # line 38
            return other | self  # line 39
        else:  # line 40
            raise _coconut_tail_call(Or, self, other)  # line 41
    @_coconut_tco  # line 42
    def __rshift__(self, other):  # line 42
        if isinstance(other, Imp):  # line 43
            return other << self  # line 44
        else:  # line 45
            raise _coconut_tail_call(Imp, self, other)  # line 46
    def __lshift__(self, other):  # line 47
        assert wff(other), other  # line 48
        return other >> self  # line 49
    @_coconut_tco  # line 50
    def __invert__(self):  # line 50
        raise _coconut_tail_call(Not, self)  # line 51
    @_coconut_tco  # line 52
    def __xor__(self, other):  # line 52
        raise _coconut_tail_call(Or, And(self, Not(other)), And(Not(self), other))  # line 53
    def __len__(self):  # line 54
        return 1  # line 54
    def __ne__(self, other):  # line 55
        return not self == other  # line 55
    def simplify(self, **kwargs):  # line 56
        """Simplify the given expression."""  # line 57
        return self  # line 58
    def substitute(self, subs):  # line 59
        """Substitutes a dictionary into the expression."""  # line 60
        return self  # line 61
    def resolve(self, **kwargs):  # line 62
        """Performs resolution on the clauses in a CNF expression."""  # line 63
        return self  # line 64
    def find_unification(self, other):  # line 65
        """Find a substitution in self that would make self into other."""  # line 66
        if self == other:  # line 67
            return {}  # line 68
        else:  # line 69
            return None  # line 70
    @_coconut_tco  # line 71
    def contradicts(self, other, **kwargs):  # line 71
        """Assuming self is simplified, determines if it contradicts other."""  # line 72
        if isinstance(other, Not):  # line 73
            raise _coconut_tail_call(other.contradicts, self, **kwargs)  # line 74
        else:  # line 75
            return self == Not(other).simplify(**kwargs)  # line 76
    @_coconut_tco  # line 77
    def resolve_against(self, other, **kwargs):  # line 77
        """Attempt to perform a resolution against other else None."""  # line 78
        if isinstance(other, (Not, Or)):  # line 79
            raise _coconut_tail_call(other.resolve_against, self, **kwargs)  # line 80
        elif (self.find_unification)(Not(other).simplify(**kwargs)) is not None:  # line 81
            return bot  # line 82
        else:  # line 83
            return None  # line 84

class Top(Expr):  # line 86
    __slots__ = ()  # line 87
    @_coconut_tco  # line 88
    def __eq__(self, other):  # line 88
        raise _coconut_tail_call(isinstance, other, Top)  # line 88
    def __repr__(self):  # line 89
        return "top"  # line 89
    def __str__(self):  # line 90
        return top_sym  # line 90
    def __bool__(self):  # line 91
        return True  # line 91
top = true = Top()  # line 92

class Bot(Expr):  # line 94
    __slots__ = ()  # line 95
    @_coconut_tco  # line 96
    def __eq__(self, other):  # line 96
        raise _coconut_tail_call(isinstance, other, Bot)  # line 96
    def __repr__(self):  # line 97
        return "bot"  # line 97
    def __str__(self):  # line 98
        return bot_sym  # line 98
    def __bool__(self):  # line 99
        return False  # line 99
bot = false = Bot()  # line 100

class Atom(Expr):  # line 102
    __slots__ = ("name",)  # line 103
    def __init__(self, name):  # line 104
        if isinstance(name, Atom):  # line 105
            name = name.name  # line 106
        assert isinstance(name, str)  # line 107
        self.name = name  # line 108
    def __repr__(self):  # line 109
        return self.__class__.__name__ + '("' + self.name + '")'  # line 110
    def __str__(self):  # line 111
        return self.name  # line 112
    def __eq__(self, other):  # line 113
        return isinstance(other, self.__class__) and self.name == other.name  # line 114
    @_coconut_tco  # line 115
    def __hash__(self):  # line 115
        raise _coconut_tail_call((hash), (self.__class__.__name__, self.name))  # line 116
    def substitute_elements(self, subs):  # line 117
        """Substitute for the elements of the Atom, not the Atom itself."""  # line 118
        return self  # line 119
    @_coconut_tco  # line 120
    def substitute(self, subs):  # line 120
        try:  # line 121
            sub = subs[self]  # line 122
        except KeyError:  # line 123
            raise _coconut_tail_call(self.substitute_elements, subs)  # line 124
        else:  # line 125
            if wff(sub):  # line 126
                return sub  # line 127
            elif sub is True:  # line 128
                return top  # line 129
            elif sub is False:  # line 130
                return bot  # line 131
            else:  # line 132
                raise TypeError("cannot perform substitution " + self + " => " + sub)  # line 133

class Proposition(Atom):  # line 135
    __slots__ = ()  # line 136
    @_coconut_tco  # line 137
    def __call__(self, *args):  # line 137
        raise _coconut_tail_call(Predicate, self.name, *args)  # line 138

class FuncAtom(Atom):  # line 140
    __slots__ = ("args",)  # line 141
    def __init__(self, name, *args):  # line 142
        super(FuncAtom, self).__init__(name)  # line 143
        for arg in args:  # line 144
            assert isinstance(arg, Term), arg  # line 145
        self.args = args  # line 146
    def __repr__(self):  # line 147
        return self.name + "(" + ", ".join((repr(x) for x in self.args)) + ")"  # line 148
    def __str__(self):  # line 149
        return self.name + "(" + ", ".join((str(x) for x in self.args)) + ")"  # line 150
    def __eq__(self, other):  # line 151
        return isinstance(other, self.__class__) and self.name == other.name and self.args == other.args  # line 152
    @_coconut_tco  # line 153
    def __hash__(self):  # line 153
        raise _coconut_tail_call((hash), (self.__class__.__name__, self.name, self.args))  # line 154
    def find_unification(self, other):  # line 155
        if isinstance(other, self.__class__) and self.name == other.name and len(self.args) == len(other.args):  # line 156
            subs = {}  # line 157
            for i, x in enumerate(self.args):  # line 158
                y = other.args[i]  # line 159
                unif = x.find_unification(y)  # line 160
                if unif is None:  # line 161
                    return None  # line 162
                for name, var in unif.items():  # line 163
                    if name not in subs:  # line 164
                        subs[name] = var  # line 165
                    elif subs[name] != var:  # line 166
                        return None  # line 167
            return subs  # line 168
        else:  # line 169
            return None  # line 170

class Predicate(FuncAtom):  # line 172
    __slots__ = ()  # line 173
    @_coconut_tco  # line 174
    def proposition(self):  # line 174
        raise _coconut_tail_call(Proposition, self.name)  # line 175
    @_coconut_tco  # line 176
    def substitute_elements(self, subs):  # line 176
        try:  # line 177
            sub = subs[self.proposition()]  # line 178
        except KeyError:  # line 179
            raise _coconut_tail_call((_coconut.functools.partial(Predicate, self.name)), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.args))  # line 180
        else:  # line 181
            raise _coconut_tail_call(Predicate, sub.name, *self.args)  # line 182

class Term(Atom):  # line 184
    __slots__ = ()  # line 185
    @_coconut_tco  # line 186
    def variable(self):  # line 186
        """Convert to a variable."""  # line 187
        assert isvar(self), self  # line 188
        raise _coconut_tail_call(Variable, self.name)  # line 189
    @_coconut_tco  # line 190
    def constant(self):  # line 190
        """Convert to a constant."""  # line 191
        assert isvar(self), self  # line 192
        raise _coconut_tail_call(Constant, self.name)  # line 193
    @_coconut_tco  # line 194
    def rename(self, name):  # line 194
        """Create a new term with a different name."""  # line 195
        raise _coconut_tail_call(self.__class__, name)  # line 196
    @_coconut_tco  # line 197
    def prime(self):  # line 197
        """Rename by adding a prime."""  # line 198
        raise _coconut_tail_call(self.rename, self.name + "'")  # line 199
    @_coconut_tco  # line 200
    def substitute(self, subs):  # line 200
        for var, sub in subs.items():  # line 201
            if isinstance(var, Term) and self.name == var.name:  # line 202
                if isvar(self) or self == var:  # line 203
                    return sub  # line 204
                else:  # line 205
                    raise _coconut_tail_call(self.rename, sub.name)  # line 206
        raise _coconut_tail_call(self.substitute_elements, subs)  # line 207

class Variable(Term):  # line 209
    __slots__ = ()  # line 210
    def variable(self):  # line 211
        return self  # line 211
    @_coconut_tco  # line 212
    def __call__(self, *args):  # line 212
        raise _coconut_tail_call(Function, self.name, *args)  # line 213
    def find_unification(self, other):  # line 214
        if isinstance(other, Term):  # line 215
            return {self: other}  # line 216
        else:  # line 217
            return None  # line 218

class Constant(Term):  # line 220
    __slots__ = ()  # line 221
    def constant(self):  # line 222
        return self  # line 222
    @_coconut_tco  # line 223
    def __call__(self, *args):  # line 223
        raise _coconut_tail_call(Function, self.name, *args)  # line 224
    def find_unification(self, other):  # line 225
        if isinstance(other, Variable):  # line 226
            return {other: self}  # line 227
        else:  # line 228
            return super(Constant, self).find_unification(other)  # line 229

class Function(Term, FuncAtom):  # line 231
    __slots__ = ()  # line 232
    @_coconut_tco  # line 233
    def substitute_elements(self, subs):  # line 233
        raise _coconut_tail_call((_coconut.functools.partial(Function, self.name)), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.args))  # line 234
    @_coconut_tco  # line 235
    def rename(self, name):  # line 235
        raise _coconut_tail_call(self.__class__, name, *self.args)  # line 236
    def find_unification(self, other):  # line 237
        if isinstance(other, Variable):  # line 238
            return {other: self}  # line 239
        else:  # line 240
            return super(Function, self).find_unification(other)  # line 241

class UnaryOp(Expr):  # line 243
    __slots__ = ("elem",)  # line 244
    def __init__(self, elem):  # line 245
        assert wff(elem), elem  # line 246
        self.elem = elem  # line 247
    def __repr__(self):  # line 248
        return self.__class__.__name__ + "(" + repr(self.elem) + ")"  # line 249
    def __eq__(self, other):  # line 250
        return isinstance(other, self.__class__) and self.elem == other.elem  # line 251
    def __str__(self):  # line 252
        return self.opstr + quote(self.elem)  # line 253
    def __len__(self):  # line 254
        return len(self.elem) + 1  # line 255
    @_coconut_tco  # line 256
    def substitute(self, subs):  # line 256
        raise _coconut_tail_call(self.__class__, self.elem.substitute(subs))  # line 257
    @_coconut_tco  # line 258
    def find_unification(self, other):  # line 258
        if isinstance(other, self.__class__):  # line 259
            raise _coconut_tail_call(self.elem.find_unification, other.elem)  # line 260
        else:  # line 261
            return None  # line 262

class Not(UnaryOp):  # line 264
    __slots__ = ()  # line 265
    opstr = not_sym  # line 266
    @property  # line 267
    def neg(self):  # line 267
        return self.elem  # line 268
    @_coconut_tco  # line 269
    def simplify(self, **kwargs):  # line 269
        if top == self.neg:  # line 270
            return bot  # line 271
        elif bot == self.neg:  # line 272
            return top  # line 273
        elif isinstance(self.neg, Not):  # line 274
            raise _coconut_tail_call(self.neg.neg.simplify, **kwargs)  # line 275
        elif isinstance(self.neg, And):  # line 276
            return Or(*map(Not, self.neg.ands)).simplify(**kwargs)  # line 277
        elif isinstance(self.neg, Or):  # line 278
            return And(*map(Not, self.neg.ors)).simplify(**kwargs)  # line 279
        elif isinstance(self.neg, Imp):  # line 280
            ands = self.neg.conds + (Not(self.neg.concl),)  # line 281
            return And(*ands).simplify(**kwargs)  # line 282
        elif isinstance(self.neg, Exists):  # line 283
            raise _coconut_tail_call(ForAll, self.neg.var, Not(self.neg.elem).simplify(**kwargs))  # line 284
        elif isinstance(self.neg, ForAll):  # line 285
            raise _coconut_tail_call(Exists, self.neg.var, Not(self.neg.elem).simplify(**kwargs))  # line 286
        else:  # line 287
            raise _coconut_tail_call(Not, self.neg.simplify(**kwargs))  # line 288
    def contradicts(self, other, **kwargs):  # line 289
        return self.neg == other  # line 290
    @_coconut_tco  # line 291
    def resolve_against(self, other, **kwargs):  # line 291
        if isinstance(other, Or):  # line 292
            raise _coconut_tail_call(other.resolve_against, self, **kwargs)  # line 293
        elif self.neg.find_unification(other) is not None:  # line 294
            return bot  # line 295
        else:  # line 296
            return None  # line 297

class Quantifier(Expr):  # line 299
    __slots__ = ("var", "elem")  # line 300
    def __repr__(self):  # line 301
        return self.__class__.__name__ + "(" + str(self.var) + ", " + repr(self.elem) + ")"  # line 302
    def __str__(self):  # line 303
        return self.opstr + str(self.var) + ". " + quote(self.elem)  # line 304
    def __len__(self):  # line 305
        return len(self.elem) + len(self.var)  # line 306
    @_coconut_tco  # line 307
    def change_var(self, var):  # line 307
        """Create an equivalent expression with a new quantified variable."""  # line 308
        raise _coconut_tail_call(self.__class__, var, self.elem.substitute({self.var: var}))  # line 309
    def __eq__(self, other):  # line 310
        if isinstance(other, self.__class__):  # line 311
            return self.elem == other.change_var(self.var).elem  # line 312
        else:  # line 313
            return False  # line 314
    @_coconut_tco  # line 315
    def substitute(self, subs):  # line 315
        try:  # line 316
            var = subs[self.var]  # line 317
        except KeyError:  # line 318
            var = self.var  # line 319
        raise _coconut_tail_call(self.__class__, var, self.elem.substitute(subs))  # line 320
    @_coconut_tco  # line 321
    def make_free_in(self, other):  # line 321
        """Makes self free in other."""  # line 322
        var = self.var  # line 323
        newvar = var.prime()  # line 324
        while other != other.substitute({var: newvar}):  # line 325
            var, newvar = newvar, newvar.prime()  # line 326
        raise _coconut_tail_call(self.change_var, var)  # line 327
    @_coconut_tco  # line 328
    def simplify(self, **kwargs):  # line 328
        simp_elem = self.elem.simplify(**kwargs)  # line 329
        if simp_elem == simp_elem.substitute({self.var: self.var.prime()}):  # line 330
            return simp_elem  # line 331
        else:  # line 332
            raise _coconut_tail_call(self.__class__, self.var, simp_elem)  # line 333

class ForAll(Quantifier):  # line 335
    __slots__ = ()  # line 336
    opstr = forall_sym  # line 337
    def __init__(self, var, elem):  # line 338
        assert wff(elem), elem  # line 339
        assert isvar(var), var  # line 340
        self.var = var.variable()  # line 341
        self.elem = elem.substitute({var: self.var.variable()})  # line 342
    def resolve(self, **kwargs):  # line 343
        kwargs["variables"] = kwargs.get("variables", ()) + (self.var,)  # line 344
        return ForAll(self.var, self.elem.resolve(**kwargs)).simplify(dnf=False, **kwargs)  # line 345
FA = ForAll  # line 346

class Exists(Quantifier):  # line 348
    __slots__ = ()  # line 349
    opstr = exists_sym  # line 350
    def __init__(self, var, elem):  # line 351
        assert wff(elem), elem  # line 352
        assert isvar(var), var  # line 353
        self.var = var.constant()  # line 354
        self.elem = elem.substitute({var: self.var.constant()})  # line 355
    def resolve(self, **kwargs):  # line 356
        variables = kwargs.get("variables")  # line 357
        if variables is None:  # line 358
            skolem_elem = self.elem  # line 359
        else:  # line 360
            skolem_var = Function(self.var.name, *variables)  # line 361
            skolem_elem = self.elem.substitute({self.var: skolem_var})  # line 362
        return Exists(self.var, skolem_elem.resolve(**kwargs)).simplify(dnf=False, **kwargs)  # line 363
TE = Exists  # line 364

class BinaryOp(Expr):  # line 366
    __slots__ = ("elems",)  # line 367
    def __init__(self, *elems):  # line 368
        assert len(elems) >= 2, elems  # line 369
        for x in elems:  # line 370
            assert wff(x), x  # line 371
        self.elems = elems  # line 372
    def __repr__(self):  # line 373
        return self.__class__.__name__ + "(" + ", ".join((repr(x) for x in self.elems)) + ")"  # line 374
    @_coconut_tco  # line 375
    def __str__(self):  # line 375
        raise _coconut_tail_call((" " + self.opstr + " ").join, (quote(x) for x in self.elems))  # line 376
    def __len__(self):  # line 377
        return sum(map(len, self.elems)) + 1  # line 378
    @_coconut_tco  # line 379
    def substitute(self, subs):  # line 379
        raise _coconut_tail_call((self.__class__), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.elems))  # line 380

class Imp(BinaryOp):  # line 382
    __slots__ = ()  # line 383
    opstr = imp_sym  # line 384
    @_coconut_tco  # line 385
    def __rshift__(self, other):  # line 385
        if isinstance(other, Imp):  # line 386
            raise _coconut_tail_call(Imp, self, *other.elems)  # line 387
        else:  # line 388
            raise _coconut_tail_call(Imp, self, other)  # line 389
    @_coconut_tco  # line 390
    def __lshift__(self, other):  # line 390
        raise _coconut_tail_call((Imp), *(other,) + self.elems)  # line 391
    @property  # line 392
    def conds(self):  # line 392
        return self.elems[:-1]  # line 393
    @property  # line 394
    def concl(self):  # line 394
        return self.elems[-1]  # line 395
    def __eq__(self, other):  # line 396
        return isinstance(other, self.__class__) and self.concl == other.concl and (unorderd_eq)(self.conds, other.conds)  # line 397
    def simplify(self, **kwargs):  # line 398
        ors = tuple(map(Not, self.conds)) + (self.concl,)  # line 399
        return Or(*ors).simplify(**kwargs)  # line 400

class BoolOp(BinaryOp):  # line 402
    __slots__ = ()  # line 403
    def __new__(cls, *elems):  # line 404
        if not elems:  # line 405
            return cls.identity  # line 406
        elif len(elems) == 1:  # line 407
            assert wff(elems[0]), elems[0]  # line 408
            return elems[0]  # sometimes returns an instance of cls  # line 409
        else:  # line 410
            return super(BoolOp, cls).__new__(cls)  # line 411
    def __init__(self, *elems):  # line 412
        if len(elems) > 1:  # __new__ should handle all other cases  # line 413
            super(BoolOp, self).__init__(*elems)  # line 414
    def __eq__(self, other):  # line 415
        return isinstance(other, self.__class__) and (unorderd_eq)(self.elems, other.elems)  # line 416
    @_coconut_tco  # line 417
    def merge(self):  # line 417
        """Merges nested copies of a boolean operator."""  # line 418
        elems = []  # line 419
        for x in self.elems:  # line 420
            if isinstance(x, self.__class__):  # line 421
                elems.extend(x.merge().elems)  # line 422
            else:  # line 423
                elems.append(x)  # line 424
        raise _coconut_tail_call(self.__class__, *elems)  # line 425
    @_coconut_tco  # line 426
    def dedupe(self):  # line 426
        """Removes duplicate elements from a boolean operator."""  # line 427
        elems = []  # line 428
        for x in self.elems:  # line 429
            if x not in elems:  # line 430
                elems.append(x)  # line 431
        raise _coconut_tail_call(self.__class__, *elems)  # line 432
    @_coconut_tco  # line 433
    def clean(self):  # line 433
        """Removes copies of the identity."""  # line 434
        raise _coconut_tail_call((self.__class__), *(_coconut.functools.partial(filter, _coconut.functools.partial(_coconut.operator.ne, self.identity)))(self.elems))  # line 435
    @_coconut_tco  # line 436
    def prenex(self, **kwargs):  # line 436
        """Pulls quantifiers out."""  # line 437
        for i, x in enumerate(self.elems):  # line 438
            if isinstance(x, Quantifier):  # line 439
                elems = self.elems[:i] + self.elems[i + 1:]  # line 440
                free_x = x.make_free_in(self.__class__(*elems))  # line 441
                elems += (free_x.elem,)  # line 442
                raise _coconut_tail_call((_coconut.functools.partial(free_x.__class__, free_x.var)), self.__class__(*elems).simplify(**kwargs))  # line 443
        return self  # line 444

class Or(BoolOp):  # line 446
    __slots__ = ()  # line 447
    opstr = or_sym  # line 448
    identity = bot  # line 449
    @_coconut_tco  # line 450
    def __or__(self, other):  # line 450
        raise _coconut_tail_call((Or), *self.elems + (other,))  # line 451
    @property  # line 452
    def ors(self):  # line 452
        return self.elems  # line 453
    def distribute(self, **kwargs):  # line 454
        """If this Or contains an And, distribute into it."""  # line 455
        for i, x in enumerate(self.ors):  # line 456
            if isinstance(x, And):  # line 457
                ands = ((Or)(*(y,) + self.ors[:i] + self.ors[i + 1:]) for y in x.ands)  # line 458
                return And(*ands).simplify(**kwargs)  # line 459
        return self  # line 460
    def simplify(self, dnf=False, debug=False, **kwargs):  # line 461
        kwargs["debug"] = debug  # line 462
        kwargs["dnf"] = dnf  # line 463
        ors = (_coconut.functools.partial(map, lambda x: x.simplify(**kwargs)))(self.merge().ors)  # line 464
        out = Or(*ors).clean()  # line 465
        if isinstance(out, Or) and not dnf:  # line 466
            out = out.distribute(**kwargs)  # line 467
        if isinstance(out, Or):  # line 468
            out = out.merge().dedupe()  # line 469
        if isinstance(out, Or) and out.tautology(**kwargs):  # line 470
            out = top  # line 471
        if isinstance(out, Or):  # line 472
            out = out.prenex(**kwargs)  # line 473
        if debug:  # line 474
            print(self, "=>", out)  # line 475
        return out  # line 476
    def tautology(self, **kwargs):  # line 477
        """Determines if the Or is a blatant tautology."""  # line 478
        for i, x in enumerate(self.ors):  # line 479
            if top == x:  # line 480
                return True  # line 481
            for y in self.ors[i + 1:]:  # line 482
                if x.contradicts(y, **kwargs):  # line 483
                    return True  # line 484
        return False  # line 485
    @_coconut_tco  # line 486
    def resolve_against(self, other, **kwargs):  # line 486
        if isinstance(other, Or):  # line 487
            not_other_ors = (_coconut.functools.partial(map, lambda x: x.simplify(**kwargs)))((_coconut.functools.partial(map, Not))(other.ors))  # line 488
            for i, x in enumerate(self.ors):  # line 489
                for j, y in enumerate(not_other_ors):  # line 490
                    subs = x.find_unification(y)  # line 491
                    if subs is not None:  # line 492
                        raise _coconut_tail_call((Or), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.ors[:i] + self.ors[i + 1:] + other.ors[:j] + other.ors[j + 1:]))  # line 493

        else:  # line 495
            not_other = Not(other).simplify(**kwargs)  # line 496
            for i, x in enumerate(self.ors):  # line 497
                subs = x.find_unification(not_other)  # line 498
                if subs is not None:  # line 499
                    raise _coconut_tail_call((Or), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.ors[:i] + self.ors[i + 1:]))  # line 500
        return None  # line 501

class And(BoolOp):  # line 503
    __slots__ = ()  # line 504
    opstr = and_sym  # line 505
    identity = top  # line 506
    @_coconut_tco  # line 507
    def __and__(self, other):  # line 507
        raise _coconut_tail_call((And), *self.elems + (other,))  # line 508
    @property  # line 509
    def ands(self):  # line 509
        return self.elems  # line 510
    def distribute(self, **kwargs):  # line 511
        """If this And contains an Or, distribute into it."""  # line 512
        for i, x in enumerate(self.ands):  # line 513
            if isinstance(x, Or):  # line 514
                ors = ((And)(*(y,) + self.ands[:i] + self.ands[i + 1:]) for y in x.ors)  # line 515
                return Or(*ors).simplify(**kwargs)  # line 516
        return self  # line 517
    def simplify(self, dnf=False, debug=False, **kwargs):  # line 518
        kwargs["debug"] = debug  # line 519
        kwargs["dnf"] = dnf  # line 520
        ands = (_coconut.functools.partial(map, lambda x: x.simplify(**kwargs)))(self.merge().ands)  # line 521
        out = And(*ands).clean()  # line 522
        if isinstance(out, And) and dnf:  # line 523
            out = out.distribute(**kwargs)  # line 524
        if isinstance(out, And):  # line 525
            out = out.merge().dedupe()  # line 526
        if isinstance(out, And) and out.contradiction(**kwargs):  # line 527
            out = bot  # line 528
        if isinstance(out, And):  # line 529
            out = out.prenex(**kwargs)  # line 530
        if debug:  # line 531
            print(self, "=>", out)  # line 532
        return out  # line 533
    def contradiction(self, **kwargs):  # line 534
        """Determines if the And is a blatant contradiction."""  # line 535
        for i, x in enumerate(self.ands):  # line 536
            if bot == x:  # line 537
                return True  # line 538
            for y in self.ands[i + 1:]:  # line 539
                if x.contradicts(y, **kwargs):  # line 540
                    return True  # line 541
        return False  # line 542
    def resolve(self, debug=False, **kwargs):  # line 543
        """Performs all possible resolutions within the And."""  # line 544
        kwargs["debug"] = debug  # line 545
        if debug:  # line 546
            print(self)  # line 547
        clauses = (list)(self.ands)  # line 548
        prev_clause_len = 1  # line 549
        while prev_clause_len < len(clauses):  # line 550
            prev_clause_len = len(clauses)  # line 551
# reversed ensures conclusions get tested first
            for i in (reversed)(range(1, len(clauses))):  # line 553
                x = clauses[i]  # line 554
                for y in clauses[:i + 1]:  # allow resolution of a clause against itself  # line 555
                    resolution = x.resolve_against(y)  # line 556
                    if resolution is not None:  # line 557
                        resolution = resolution.simplify(dnf=False, **kwargs)  # line 558
                        if debug:  # line 559
                            print(x, "+", y, "=>", resolution)  # line 560
                        if isinstance(resolution, And):  # line 561
                            new_clauses = resolution.ands  # line 562
                        else:  # line 563
                            new_clauses = (resolution,)  # line 564
                        for y in new_clauses:  # line 565
                            if y == bot:  # line 566
                                return bot  # line 567
                            elif y not in clauses:  # line 568
                                clauses.append(y)  # line 569
        return And(*clauses).simplify(dnf=False, **kwargs)  # line 570
