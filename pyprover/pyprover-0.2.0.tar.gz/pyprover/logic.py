#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x3fc441a1

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
from pyprover.util import quote  # line 4
from pyprover.util import log_simplification  # line 13

# Functions:

def wff(expr):  # line 20
    """Determines whether expr is a well-formed formula."""  # line 22
    return isinstance(expr, Expr) and not isinstance(expr, Term)  # line 23

@_coconut_tco  # line 24
def isvar(var):  # line 24
    """Whether a term is a variable."""  # line 26
    raise _coconut_tail_call(isinstance, var, (Constant, Variable))  # line 27

# Classes:

class Expr(_coconut.object):  # line 31
    __slots__ = ()  # line 32
    @_coconut_tco  # line 33
    def __and__(self, other):  # line 33
        if isinstance(other, And):  # line 34
            return other & self  # line 35
        else:  # line 36
            raise _coconut_tail_call(And, self, other)  # line 37
    @_coconut_tco  # line 38
    def __or__(self, other):  # line 38
        if isinstance(other, Or):  # line 39
            return other | self  # line 40
        else:  # line 41
            raise _coconut_tail_call(Or, self, other)  # line 42
    @_coconut_tco  # line 43
    def __rshift__(self, other):  # line 43
        if isinstance(other, Imp):  # line 44
            return other << self  # line 45
        else:  # line 46
            raise _coconut_tail_call(Imp, self, other)  # line 47
    def __lshift__(self, other):  # line 48
        assert wff(other), other  # line 49
        return other >> self  # line 50
    @_coconut_tco  # line 51
    def __invert__(self):  # line 51
        raise _coconut_tail_call(Not, self)  # line 52
    @_coconut_tco  # line 53
    def __xor__(self, other):  # line 53
        raise _coconut_tail_call(Or, And(self, Not(other)), And(Not(self), other))  # line 54
    def __len__(self):  # line 55
        return 1  # line 55
    def __ne__(self, other):  # line 56
        return not self == other  # line 56
    def simplify(self, **kwargs):  # line 57
        """Simplify the given expression."""  # line 58
        return self  # line 59
    def substitute(self, subs):  # line 60
        """Substitutes a dictionary into the expression."""  # line 61
        return self  # line 62
    def resolve(self, **kwargs):  # line 63
        """Performs resolution on the clauses in a CNF expression."""  # line 64
        return self  # line 65
    def find_unification(self, other):  # line 66
        """Find a substitution in self that would make self into other."""  # line 67
        if self == other:  # line 68
            return {}  # line 69
        else:  # line 70
            return None  # line 71
    @_coconut_tco  # line 72
    def contradicts(self, other, **kwargs):  # line 72
        """Assuming self is simplified, determines if it contradicts other."""  # line 73
        if isinstance(other, Not):  # line 74
            raise _coconut_tail_call(other.contradicts, self, **kwargs)  # line 75
        else:  # line 76
            return self == Not(other).simplify(**kwargs)  # line 77
    @_coconut_tco  # line 78
    def resolve_against(self, other, **kwargs):  # line 78
        """Attempt to perform a resolution against other else None."""  # line 79
        if isinstance(other, (Not, Or)):  # line 80
            raise _coconut_tail_call(other.resolve_against, self, **kwargs)  # line 81
        elif (self.find_unification)(Not(other).simplify(**kwargs)) is not None:  # line 82
            return bot  # line 83
        else:  # line 84
            return None  # line 85

class Top(Expr):  # line 87
    __slots__ = ()  # line 88
    @_coconut_tco  # line 89
    def __eq__(self, other):  # line 89
        raise _coconut_tail_call(isinstance, other, Top)  # line 89
    def __repr__(self):  # line 90
        return "top"  # line 90
    def __str__(self):  # line 91
        return top_sym  # line 91
    def __bool__(self):  # line 92
        return True  # line 92
top = true = Top()  # line 93

class Bot(Expr):  # line 95
    __slots__ = ()  # line 96
    @_coconut_tco  # line 97
    def __eq__(self, other):  # line 97
        raise _coconut_tail_call(isinstance, other, Bot)  # line 97
    def __repr__(self):  # line 98
        return "bot"  # line 98
    def __str__(self):  # line 99
        return bot_sym  # line 99
    def __bool__(self):  # line 100
        return False  # line 100
bot = false = Bot()  # line 101

class Atom(Expr):  # line 103
    __slots__ = ("name",)  # line 104
    def __init__(self, name):  # line 105
        if isinstance(name, Atom):  # line 106
            name = name.name  # line 107
        assert isinstance(name, str)  # line 108
        self.name = name  # line 109
    def __repr__(self):  # line 110
        return self.__class__.__name__ + '("' + self.name + '")'  # line 111
    def __str__(self):  # line 112
        return self.name  # line 113
    def __eq__(self, other):  # line 114
        return isinstance(other, self.__class__) and self.name == other.name  # line 115
    @_coconut_tco  # line 116
    def __hash__(self):  # line 116
        raise _coconut_tail_call((hash), (self.__class__.__name__, self.name))  # line 117
    def substitute_elements(self, subs):  # line 118
        """Substitute for the elements of the Atom, not the Atom itself."""  # line 119
        return self  # line 120
    @_coconut_tco  # line 121
    def substitute(self, subs):  # line 121
        try:  # line 122
            sub = subs[self]  # line 123
        except KeyError:  # line 124
            raise _coconut_tail_call(self.substitute_elements, subs)  # line 125
        else:  # line 126
            if wff(sub):  # line 127
                return sub  # line 128
            elif sub is True:  # line 129
                return top  # line 130
            elif sub is False:  # line 131
                return bot  # line 132
            else:  # line 133
                raise TypeError("cannot perform substitution " + self + " => " + sub)  # line 134

class Proposition(Atom):  # line 136
    __slots__ = ()  # line 137
    @_coconut_tco  # line 138
    def __call__(self, *args):  # line 138
        raise _coconut_tail_call(Predicate, self.name, *args)  # line 139

class FuncAtom(Atom):  # line 141
    __slots__ = ("args",)  # line 142
    def __init__(self, name, *args):  # line 143
        super(FuncAtom, self).__init__(name)  # line 144
        for arg in args:  # line 145
            assert isinstance(arg, Term), arg  # line 146
        self.args = args  # line 147
    def __repr__(self):  # line 148
        return self.name + "(" + ", ".join((repr(x) for x in self.args)) + ")"  # line 149
    def __str__(self):  # line 150
        return self.name + "(" + ", ".join((str(x) for x in self.args)) + ")"  # line 151
    def __eq__(self, other):  # line 152
        return isinstance(other, self.__class__) and self.name == other.name and self.args == other.args  # line 153
    @_coconut_tco  # line 154
    def __hash__(self):  # line 154
        raise _coconut_tail_call((hash), (self.__class__.__name__, self.name, self.args))  # line 155
    def find_unification(self, other):  # line 156
        if isinstance(other, self.__class__) and self.name == other.name and len(self.args) == len(other.args):  # line 157
            subs = {}  # line 158
            for i, x in enumerate(self.args):  # line 159
                y = other.args[i]  # line 160
                unif = x.find_unification(y)  # line 161
                if unif is None:  # line 162
                    return None  # line 163
                for name, var in unif.items():  # line 164
                    if name not in subs:  # line 165
                        subs[name] = var  # line 166
                    elif subs[name] != var:  # line 167
                        return None  # line 168
            return subs  # line 169
        else:  # line 170
            return None  # line 171

class Predicate(FuncAtom):  # line 173
    __slots__ = ()  # line 174
    @_coconut_tco  # line 175
    def proposition(self):  # line 175
        raise _coconut_tail_call(Proposition, self.name)  # line 176
    @_coconut_tco  # line 177
    def substitute_elements(self, subs):  # line 177
        try:  # line 178
            sub = subs[self.proposition()]  # line 179
        except KeyError:  # line 180
            raise _coconut_tail_call((_coconut.functools.partial(Predicate, self.name)), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.args))  # line 181
        else:  # line 182
            raise _coconut_tail_call(Predicate, sub.name, *self.args)  # line 183

class Term(Atom):  # line 185
    __slots__ = ()  # line 186
    @_coconut_tco  # line 187
    def variable(self):  # line 187
        """Convert to a variable."""  # line 188
        raise _coconut_tail_call(Variable, self.name)  # line 189
    @_coconut_tco  # line 190
    def constant(self):  # line 190
        """Convert to a constant."""  # line 191
        raise _coconut_tail_call(Constant, self.name)  # line 192
    @_coconut_tco  # line 193
    def rename(self, name):  # line 193
        """Create a new term with a different name."""  # line 194
        raise _coconut_tail_call(self.__class__, name)  # line 195
    @_coconut_tco  # line 196
    def prime(self):  # line 196
        """Rename by adding a prime."""  # line 197
        raise _coconut_tail_call(self.rename, self.name + "'")  # line 198
    @_coconut_tco  # line 199
    def substitute(self, subs):  # line 199
        for var, sub in subs.items():  # line 200
            if isinstance(var, Term) and self.name == var.name:  # line 201
                if isvar(self) or self == var:  # line 202
                    return sub  # line 203
                else:  # line 204
                    raise _coconut_tail_call(self.rename, sub.name)  # line 205
        raise _coconut_tail_call(self.substitute_elements, subs)  # line 206

class Var(Term):  # line 208
    __slots__ = ()  # line 209
    def variable(self):  # line 210
        return self  # line 210
    @_coconut_tco  # line 211
    def __call__(self, *args):  # line 211
        raise _coconut_tail_call(Function, self.name, *args)  # line 212
    def find_unification(self, other):  # line 213
        if isinstance(other, Term):  # line 214
            return {self: other}  # line 215
        else:  # line 216
            return None  # line 217
Variable = Var  # line 218

class Const(Term):  # line 220
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
Constant = Const  # line 230

class Function(Term, FuncAtom):  # line 232
    __slots__ = ()  # line 233
    @_coconut_tco  # line 234
    def substitute_elements(self, subs):  # line 234
        raise _coconut_tail_call((_coconut.functools.partial(Function, self.name)), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.args))  # line 235
    @_coconut_tco  # line 236
    def rename(self, name):  # line 236
        raise _coconut_tail_call(self.__class__, name, *self.args)  # line 237
    def find_unification(self, other):  # line 238
        if isinstance(other, Variable):  # line 239
            return {other: self}  # line 240
        else:  # line 241
            return super(Function, self).find_unification(other)  # line 242

class UnaryOp(Expr):  # line 244
    __slots__ = ("elem",)  # line 245
    def __init__(self, elem):  # line 246
        assert wff(elem), elem  # line 247
        self.elem = elem  # line 248
    def __repr__(self):  # line 249
        return self.__class__.__name__ + "(" + repr(self.elem) + ")"  # line 250
    def __eq__(self, other):  # line 251
        return isinstance(other, self.__class__) and self.elem == other.elem  # line 252
    def __str__(self):  # line 253
        return self.opstr + quote(self.elem)  # line 254
    def __len__(self):  # line 255
        return len(self.elem) + 1  # line 256
    @_coconut_tco  # line 257
    def substitute(self, subs):  # line 257
        raise _coconut_tail_call(self.__class__, self.elem.substitute(subs))  # line 258
    @_coconut_tco  # line 259
    def find_unification(self, other):  # line 259
        if isinstance(other, self.__class__):  # line 260
            raise _coconut_tail_call(self.elem.find_unification, other.elem)  # line 261
        else:  # line 262
            return None  # line 263
    def resolve(self, **kwargs):  # line 264
        return self.__class__(self.elem.resolve(**kwargs)).simplify(**kwargs)  # line 265

class Not(UnaryOp):  # line 267
    __slots__ = ()  # line 268
    opstr = not_sym  # line 269
    @property  # line 270
    def neg(self):  # line 270
        return self.elem  # line 271
    @_coconut_tco  # line 272
    def simplify(self, **kwargs):  # line 272
        if top == self.neg:  # line 273
            return bot  # line 274
        elif bot == self.neg:  # line 275
            return top  # line 276
        elif isinstance(self.neg, Not):  # line 277
            raise _coconut_tail_call(self.neg.neg.simplify, **kwargs)  # line 278
        elif isinstance(self.neg, And):  # line 279
            return Or(*map(Not, self.neg.ands)).simplify(**kwargs)  # line 280
        elif isinstance(self.neg, Or):  # line 281
            return And(*map(Not, self.neg.ors)).simplify(**kwargs)  # line 282
        elif isinstance(self.neg, Imp):  # line 283
            ands = self.neg.conds + (Not(self.neg.concl),)  # line 284
            return And(*ands).simplify(**kwargs)  # line 285
        elif isinstance(self.neg, Exists):  # line 286
            raise _coconut_tail_call(ForAll, self.neg.var, Not(self.neg.elem).simplify(**kwargs))  # line 287
        elif isinstance(self.neg, ForAll):  # line 288
            raise _coconut_tail_call(Exists, self.neg.var, Not(self.neg.elem).simplify(**kwargs))  # line 289
        else:  # line 290
            raise _coconut_tail_call(Not, self.neg.simplify(**kwargs))  # line 291
    def contradicts(self, other, **kwargs):  # line 292
        return self.neg == other  # line 293
    @_coconut_tco  # line 294
    def resolve_against(self, other, **kwargs):  # line 294
        if isinstance(other, Or):  # line 295
            raise _coconut_tail_call(other.resolve_against, self, **kwargs)  # line 296
        elif self.neg.find_unification(other) is not None:  # line 297
            return bot  # line 298
        else:  # line 299
            return None  # line 300

class Quantifier(Expr):  # line 302
    __slots__ = ("var", "elem")  # line 303
    def __repr__(self):  # line 304
        return self.__class__.__name__ + "(" + str(self.var) + ", " + repr(self.elem) + ")"  # line 305
    def __str__(self):  # line 306
        return self.opstr + str(self.var) + ". " + quote(self.elem)  # line 307
    def __len__(self):  # line 308
        return len(self.elem) + len(self.var)  # line 309
    @_coconut_tco  # line 310
    def change_var(self, var):  # line 310
        """Create an equivalent expression with a new quantified variable."""  # line 311
        raise _coconut_tail_call(self.__class__, var, self.elem.substitute({self.var: var}))  # line 312
    @_coconut_tco  # line 313
    def change_elem(self, elem):  # line 313
        """Create an equivalent quantifier with a new expression."""  # line 314
        raise _coconut_tail_call(self.__class__, self.var, elem)  # line 315
    def __eq__(self, other):  # line 316
        if isinstance(other, self.__class__):  # line 317
            return self.elem == other.change_var(self.var).elem  # line 318
        else:  # line 319
            return False  # line 320
    @_coconut_tco  # line 321
    def substitute(self, subs):  # line 321
        raise _coconut_tail_call(self.__class__, self.var.substitute(subs).constant(), self.elem.substitute(subs))  # line 322
    @_coconut_tco  # line 323
    def make_free_in(self, other):  # line 323
        """Makes self free in other."""  # line 324
        var = self.var  # line 325
        newvar = var.prime()  # line 326
        while other != other.substitute({var: newvar}):  # line 327
            var, newvar = newvar, newvar.prime()  # line 328
        raise _coconut_tail_call(self.change_var, var)  # line 329
    def find_unification(self, other):  # line 330
        return self.make_free_in(other).elem.find_unification(other)  # line 331
    @_coconut_tco  # line 332
    def resolve_against(self, other, **kwargs):  # line 332
        if isinstance(other, Quantifier):  # line 333
            resolution = (_coconut.functools.partial(self.elem.resolve_against, **kwargs))(Not(other.elem).simplify(**kwargs))  # line 334
            if resolution is None:  # line 335
                return None  # line 336
            elif isinstance(other, ForAll):  # don't pull an Exists out of a ForAll  # line 337
                raise _coconut_tail_call((other.change_elem), (self.change_elem)(resolution))  # line 338
            else:  # line 339
                raise _coconut_tail_call((self.change_elem), (other.change_elem)(resolution))  # line 340
        else:  # line 341
            return super(Quantifier, self).resolve_against(other, **kwargs)  # line 342

class ForAll(Quantifier):  # line 344
    __slots__ = ()  # line 345
    opstr = forall_sym  # line 346
    def __init__(self, var, elem):  # line 347
        assert wff(elem), elem  # line 348
        assert isvar(var), var  # line 349
        self.var = var.variable()  # line 350
        self.elem = elem.substitute({var: self.var.variable()})  # line 351
    def simplify(self, **kwargs):  # line 352
        kwargs["in_forall"] = True  # line 353
        return self.__class__(self.var, self.elem.simplify(**kwargs)).drop_quantifier(**kwargs)  # line 354
    def resolve(self, **kwargs):  # line 355
        kwargs["in_forall"] = True  # line 356
        kwargs["variables"] = kwargs.get("variables", ()) + (self.var,)  # line 357
        return ForAll(self.var, self.elem.resolve(**kwargs)).simplify(dnf=False, **kwargs)  # line 358
    def drop_quantifier(self, nonempty_universe=True, **kwargs):  # line 359
        kwargs["nonempty_universe"] = nonempty_universe  # line 360
        if not nonempty_universe:  # line 361
            elem = self.elem  # line 362
            while isinstance(elem, Exists):  # line 363
                elem = elem.elem  # line 364
            if top == elem:  # line 365
                return elem  # line 366
        elif self.elem == self.elem.substitute({self.var: self.var.prime()}):  # line 367
            return self.elem  # line 368
        return self  # line 369
FA = ForAll  # line 370

class Exists(Quantifier):  # line 372
    __slots__ = ()  # line 373
    opstr = exists_sym  # line 374
    def __init__(self, var, elem):  # line 375
        assert wff(elem), elem  # line 376
        assert isvar(var), var  # line 377
        self.var = var.constant()  # line 378
        self.elem = elem.substitute({var: self.var.constant()})  # line 379
    def simplify(self, **kwargs):  # line 380
        kwargs["in_exists"] = True  # line 381
        return self.__class__(self.var, self.elem.simplify(**kwargs)).drop_quantifier(**kwargs)  # line 382
    def resolve(self, **kwargs):  # line 383
        kwargs["in_exists"] = True  # line 384
        variables = kwargs.get("variables")  # line 385
        if variables is None:  # line 386
            skolem_elem = self.elem  # line 387
        else:  # line 388
            skolem_var = Function(self.var.name, *variables)  # line 389
            skolem_elem = self.elem.substitute({self.var: skolem_var})  # line 390
        return Exists(self.var, skolem_elem.resolve(**kwargs)).simplify(dnf=False, **kwargs)  # line 391
    def drop_quantifier(self, nonempty_universe=True, **kwargs):  # line 392
        kwargs["nonempty_universe"] = nonempty_universe  # line 393
        if not nonempty_universe:  # line 394
            elem = self.elem  # line 395
            while isinstance(elem, ForAll):  # line 396
                elem = elem.elem  # line 397
            if bot == elem:  # line 398
                return elem  # line 399
        elif self.elem == self.elem.substitute({self.var: self.var.prime()}):  # line 400
            return self.elem  # line 401
        return self  # line 402
TE = Exists  # line 403

class BinaryOp(Expr):  # line 405
    __slots__ = ("elems",)  # line 406
    identity = None  # line 407
    def __new__(cls, *elems):  # line 408
        if not elems:  # line 409
            if cls.identity is None:  # line 410
                raise TypeError(cls.__name__ + " requires at least one argument")  # line 411
            else:  # line 412
                return cls.identity  # line 413
        elif len(elems) == 1:  # line 414
            assert wff(elems[0]), elems[0]  # line 415
            return elems[0]  # sometimes returns an instance of cls  # line 416
        else:  # line 417
            return super(BinaryOp, cls).__new__(cls)  # line 418
    def __init__(self, *elems):  # line 419
        if len(elems) > 1:  # __new__ should handle all other cases  # line 420
            assert len(elems) >= 2, elems  # line 421
            for x in elems:  # line 422
                assert wff(x), x  # line 423
            self.elems = elems  # line 424
    def __repr__(self):  # line 425
        return self.__class__.__name__ + "(" + ", ".join((repr(x) for x in self.elems)) + ")"  # line 426
    @_coconut_tco  # line 427
    def __str__(self):  # line 427
        raise _coconut_tail_call((" " + self.opstr + " ").join, (quote(x) for x in self.elems))  # line 428
    def __len__(self):  # line 429
        return sum(map(len, self.elems)) + 1  # line 430
    @_coconut_tco  # line 431
    def substitute(self, subs):  # line 431
        raise _coconut_tail_call((self.__class__), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.elems))  # line 432
    def resolve(self, **kwargs):  # line 433
        elems = (_coconut.functools.partial(map, lambda x: x.resolve(**kwargs)))(self.elems)  # line 434
        return self.__class__(*elems).simplify(**kwargs)  # line 435

class Imp(BinaryOp):  # line 437
    __slots__ = ()  # line 438
    opstr = imp_sym  # line 439
    @_coconut_tco  # line 440
    def __rshift__(self, other):  # line 440
        if isinstance(other, Imp):  # line 441
            raise _coconut_tail_call(Imp, self, *other.elems)  # line 442
        else:  # line 443
            raise _coconut_tail_call(Imp, self, other)  # line 444
    @_coconut_tco  # line 445
    def __lshift__(self, other):  # line 445
        raise _coconut_tail_call((Imp), *(other,) + self.elems)  # line 446
    @property  # line 447
    def conds(self):  # line 447
        return self.elems[:-1]  # line 448
    @property  # line 449
    def concl(self):  # line 449
        return self.elems[-1]  # line 450
    def __eq__(self, other):  # line 451
        return isinstance(other, self.__class__) and self.concl == other.concl and (unorderd_eq)(self.conds, other.conds)  # line 452
    def simplify(self, **kwargs):  # line 453
        ors = tuple(map(Not, self.conds)) + (self.concl,)  # line 454
        return Or(*ors).simplify(**kwargs)  # line 455

class BoolOp(BinaryOp):  # line 457
    __slots__ = ()  # line 458
    def __eq__(self, other):  # line 459
        return isinstance(other, self.__class__) and (unorderd_eq)(self.elems, other.elems)  # line 460
    @_coconut_tco  # line 461
    def merge(self):  # line 461
        """Merges nested copies of a boolean operator."""  # line 462
        elems = []  # line 463
        for x in self.elems:  # line 464
            if isinstance(x, self.__class__):  # line 465
                elems.extend(x.merge().elems)  # line 466
            else:  # line 467
                elems.append(x)  # line 468
        raise _coconut_tail_call(self.__class__, *elems)  # line 469
    @_coconut_tco  # line 470
    def dedupe(self):  # line 470
        """Removes duplicate elements from a boolean operator."""  # line 471
        elems = []  # line 472
        for x in self.elems:  # line 473
            if x not in elems:  # line 474
                elems.append(x)  # line 475
        raise _coconut_tail_call(self.__class__, *elems)  # line 476
    @_coconut_tco  # line 477
    def clean(self):  # line 477
        """Removes copies of the identity."""  # line 478
        raise _coconut_tail_call((self.__class__), *(_coconut.functools.partial(filter, _coconut.functools.partial(_coconut.operator.ne, self.identity)))(self.elems))  # line 479
    def prenex(self, **kwargs):  # line 480
        """Pulls quantifiers out."""  # line 481
        for i, x in enumerate(self.elems):  # line 482
            if isinstance(x, Quantifier) and self.can_prenex(x, **kwargs):  # line 483
                elems = self.elems[:i] + self.elems[i + 1:]  # line 484
                free_x = x.make_free_in(self.__class__(*elems))  # line 485
                elems += (free_x.elem,)  # line 486
                return free_x.change_elem(self.__class__(*elems)).simplify(**kwargs)  # line 487
        return self  # line 488

class Or(BoolOp):  # line 490
    __slots__ = ()  # line 491
    opstr = or_sym  # line 492
    identity = bot  # line 493
    @_coconut_tco  # line 494
    def __or__(self, other):  # line 494
        raise _coconut_tail_call((Or), *self.elems + (other,))  # line 495
    @property  # line 496
    def ors(self):  # line 496
        return self.elems  # line 497
    def distribute(self, **kwargs):  # line 498
        """If this Or contains an And, distribute into it."""  # line 499
        for i, x in enumerate(self.ors):  # line 500
            if isinstance(x, And):  # line 501
                ands = ((Or)(*(y,) + self.ors[:i] + self.ors[i + 1:]) for y in x.ands)  # line 502
                return And(*ands).simplify(**kwargs)  # line 503
        return self  # line 504
    def simplify(self, dnf=False, **kwargs):  # line 505
        kwargs["dnf"] = dnf  # line 506
        ors = (_coconut.functools.partial(map, lambda x: x.simplify(**kwargs)))(self.merge().ors)  # line 507
        out = Or(*ors).clean()  # line 508
        if isinstance(out, Or) and not dnf:  # line 509
            out = out.distribute(**kwargs)  # line 510
        if isinstance(out, Or):  # line 511
            out = out.merge().dedupe()  # line 512
        if isinstance(out, Or) and out.tautology(**kwargs):  # line 513
            out = top  # line 514
        if isinstance(out, Or):  # line 515
            out = out.prenex(**kwargs)  # line 516
        log_simplification(self, out, **kwargs)  # line 517
        return out  # line 518
    def tautology(self, **kwargs):  # line 519
        """Determines if the Or is a blatant tautology."""  # line 520
        for i, x in enumerate(self.ors):  # line 521
            if top == x:  # line 522
                return True  # line 523
            for y in self.ors[i + 1:]:  # line 524
                if x.contradicts(y, **kwargs):  # line 525
                    return True  # line 526
        return False  # line 527
    def can_prenex(self, other, nonempty_universe=True, in_forall=False, **kwargs):  # line 528
        kwargs["nonempty_universe"], kwargs["in_forall"] = nonempty_universe, in_forall  # line 529
        return (nonempty_universe or in_forall or not isinstance(other, Exists) or all((isinstance(x, Exists) for x in self.elems)))  # line 530
    @_coconut_tco  # line 531
    def resolve_against(self, other, **kwargs):  # line 534
        if isinstance(other, Or):  # line 535
            not_other_ors = (_coconut.functools.partial(map, lambda x: x.simplify(**kwargs)))((_coconut.functools.partial(map, Not))(other.ors))  # line 536
            for i, x in enumerate(self.ors):  # line 537
                for j, y in enumerate(not_other_ors):  # line 538
                    subs = x.find_unification(y)  # line 539
                    if subs is not None:  # line 540
                        raise _coconut_tail_call((Or), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.ors[:i] + self.ors[i + 1:] + other.ors[:j] + other.ors[j + 1:]))  # line 541
        else:  # line 542
            not_other = Not(other).simplify(**kwargs)  # line 543
            for i, x in enumerate(self.ors):  # line 544
                subs = x.find_unification(not_other)  # line 545
                if subs is not None:  # line 546
                    raise _coconut_tail_call((Or), *(_coconut.functools.partial(map, _coconut.operator.methodcaller("substitute", subs)))(self.ors[:i] + self.ors[i + 1:]))  # line 547
        return None  # line 548

class And(BoolOp):  # line 550
    __slots__ = ()  # line 551
    opstr = and_sym  # line 552
    identity = top  # line 553
    @_coconut_tco  # line 554
    def __and__(self, other):  # line 554
        raise _coconut_tail_call((And), *self.elems + (other,))  # line 555
    @property  # line 556
    def ands(self):  # line 556
        return self.elems  # line 557
    def distribute(self, **kwargs):  # line 558
        """If this And contains an Or, distribute into it."""  # line 559
        for i, x in enumerate(self.ands):  # line 560
            if isinstance(x, Or):  # line 561
                ors = ((And)(*(y,) + self.ands[:i] + self.ands[i + 1:]) for y in x.ors)  # line 562
                return Or(*ors).simplify(**kwargs)  # line 563
        return self  # line 564
    def simplify(self, dnf=False, **kwargs):  # line 565
        kwargs["dnf"] = dnf  # line 566
        ands = (_coconut.functools.partial(map, lambda x: x.simplify(**kwargs)))(self.merge().ands)  # line 567
        out = And(*ands).clean()  # line 568
        if isinstance(out, And) and dnf:  # line 569
            out = out.distribute(**kwargs)  # line 570
        if isinstance(out, And):  # line 571
            out = out.merge().dedupe()  # line 572
        if isinstance(out, And) and out.contradiction(**kwargs):  # line 573
            out = bot  # line 574
        if isinstance(out, And):  # line 575
            out = out.prenex(**kwargs)  # line 576
        log_simplification(self, out, **kwargs)  # line 577
        return out  # line 578
    def contradiction(self, **kwargs):  # line 579
        """Determines if the And is a blatant contradiction."""  # line 580
        for i, x in enumerate(self.ands):  # line 581
            if bot == x:  # line 582
                return True  # line 583
            for y in self.ands[i + 1:]:  # line 584
                if x.contradicts(y, **kwargs):  # line 585
                    return True  # line 586
        return False  # line 587
    def can_prenex(self, other, nonempty_universe=True, in_exists=False, **kwargs):  # line 588
        kwargs["nonempty_universe"], kwargs["in_exists"] = nonempty_universe, in_exists  # line 589
        return (nonempty_universe or in_exists or not isinstance(other, ForAll) or all((isinstance(x, ForAll) for x in self.elems)))  # line 590
    @_coconut_tco  # line 591
    def resolve(self, debug=False, **kwargs):  # line 594
        """Performs all possible resolutions within the And."""  # line 595
        kwargs["debug"] = debug  # line 596
        resolved = super(And, self).resolve(**kwargs)  # line 597
        if not isinstance(resolved, And):  # line 598
            log_simplification(self, resolved, **kwargs)  # line 599
            return resolved  # line 600
        clauses = (list)(resolved.ands)  # line 601
        quantifiers = []  # line 602
        prev_clause_len = 1  # line 603
        while prev_clause_len < len(clauses):  # line 604
            prev_clause_len = len(clauses)  # line 605
# reversed ensures conclusions get tested first
            for i in (reversed)(range(1, len(clauses))):  # line 607
                x = clauses[i]  # line 608
                for y in clauses[:i + 1]:  # allow resolution of a clause against itself  # line 609
                    resolution = x.resolve_against(y)  # line 610
                    if resolution is not None:  # line 611
                        resolution = resolution.simplify(dnf=False, **kwargs)  # line 612
                        if debug:  # line 613
                            print(x, "+", y, "=>", resolution)  # line 614
                        new_quantifiers = []  # line 615
                        while isinstance(resolution, Quantifier) and self.can_prenex(resolution, **kwargs):  # line 616
                            (new_quantifiers.append)(resolution.change_elem)  # line 617
                            resolution = resolution.elem  # line 618
                        if isinstance(resolution, And):  # line 619
                            new_clauses = resolution.ands  # line 620
                        else:  # line 621
                            new_clauses = (resolution,)  # line 622
                        if bot in new_clauses:  # line 623
                            quantifiers.extend(new_quantifiers)  # line 624
                            clauses = [bot]  # line 625
                            break  # line 626
                        novel = False  # line 627
                        for new_clause in new_clauses:  # line 628
                            if new_clause != top and new_clause not in clauses:  # line 629
                                clauses.append(new_clause)  # line 630
                                novel = True  # line 631
                        if novel:  # line 632
                            quantifiers.extend(new_quantifiers)  # line 633
                if clauses == [bot]:  # line 634
                    break  # line 635
        resolved = reduce(_coconut_pipe, [And(*clauses)] + quantifiers)  # line 636
        log_simplification(self, resolved, **kwargs)  # line 637
        raise _coconut_tail_call(resolved.simplify, dnf=False, **kwargs)  # line 638
