# -*- coding: utf-8 -*-
# Copyright (C) 2001-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Divisor_Dag
#
# Purpose
#    Compute directed acyclic graph of all divisors of a number
#
# Revision Dates
#    24-Mar-2001 (CT)  Creation
#    28-Mar-2001 (CT)  Various optimizations and simplifications added
#     5-Apr-2001 (ARU) Computed attribute `nodes` added
#                      Bug in `__getattr__` of `_divisors` corrected
#    11-Jun-2003 (CT)  s/== None/is None/
#    11-Feb-2006 (CT)  Moved into package `TFL`
#    27-Nov-2011 (CT)  Modernize
#    11-Oct-2016 (CT)  Import `Command_Line` from `_TFL.Command_Line`
#    ««revision-date»»···
#--

from   __future__                 import print_function

from   _TFL                       import TFL

from   _TFL.primes_4              import primes
from   _TFL.pyk                   import pyk
from   _TFL._Meta.totally_ordered import totally_ordered

import math

class OverflowError (ValueError) : pass

def Divisor_Dag (n) :
    """Returns `Divisor_Dag` for `n`"""
    try :
        return _Divisor_Dag_.Table [n]
    except KeyError :
        return _Divisor_Dag_       (n)
# end def Divisor_Dag

@totally_ordered
class _Divisor_Dag_ :
    """Directed acyclic graph of all divisors of a number.

       Provides the attributes:

       number        Number to which divisor DAG applies
       subdags       Sub DAGS of divisor DAG
       divisors      Sorted list of all divisors of `number`
       prime_factors Sorted list of all prime factors of `number`
       edges         Inversely sorted list of all edges of divisor DAG
       _divisors     Dictionary of all `divisors`
       _edges        Dictionary of all `edges`
    """

    Table = {}

    def __init__ (self, n) :
        if n < 1 :
            raise ValueError (n, "must be > 0")
        self.Table [n]  = self
        self.number     = n
        self.subdags    = []
        add             = self.subdags.append
        if n in primes :
            add (Divisor_Dag (1))
        elif n > 1 :
            for p in primes.u_factors (n) :
                add (Divisor_Dag (n // p))
    # end def __init__

    def has_divisor (self, d) :
        return d in self._divisors
    # end def has_divisor

    def as_string (self, head = "    ", level = 0, seen = None) :
        if seen is None :
            seen = set ()
        results  = ["%s%s" % (head * level, self.number)]
        if self in seen :
            results [0] = "%s..." % (results [0], )
        else :
            add   = results.append
            level = level + 1
            for sd in self.subdags :
                add (sd.as_string (head, level, seen))
        seen.add (self)
        return "\n".join (results)
    # end def as_string

    def _depth_first_list (self, V, dfl) :
        if self.number in V :
            return
        V [self.number] = 1
        for sd in self.subdags :
            sd._depth_first_list (V, dfl)
        dfl.append (self)
    # end def _depth_first_list

    def depth_first_list (self) :
        # depth first list in post order
        V = {}
        dfl = []
        self._depth_first_list (V, dfl)
        return dfl
    # end def depth_first_list

    def _get_divisors (self) :
        result = {self.number : 1}
        for sd in self.subdags :
            result.update (sd._divisors)
        return result
    # end def _get_divisors

    def _get_edges (self) :
        result = {}
        for sd in self.subdags :
            result [(self, sd)] = 1
            result.update (sd._edges)
        return result
    # end def _get_edges

    def __getattr__ (self, name) :
        if name == "_divisors" :
            result = self._divisors = self._get_divisors ()
        elif name == "divisors" :
            result = self.divisors = sorted (self._divisors)
        elif name == "prime_factors" :
            result = self.prime_factors = \
                sorted (d for d in self._divisors if primes.is_prime (d))
        elif name == "_edges" :
            ### just to cash edges as dictionary
            result = self._edges = self._get_edges ()
        elif name == "edges" :
            ### use cached edge dictionary
            result = self.edges = list (self._edges)
            result.sort    ()
            result.reverse ()
        elif name == "nodes" :
            result = self.nodes = self.depth_first_list ()
        else :
            raise AttributeError (name)
        return result
    # end def _add_subdag

    def __str__ (self) :
        return "%s : %s" % (self.number, list (x.number for x in self.subdags))
    # end def __str__

    def __repr__ (self) :
        return str (self.number)
    # end def __repr__

    def __eq__ (self, other) :
        if isinstance (other, _Divisor_Dag_) :
            other = other.number
        return self.number == other
    # end def __eq__

    def __hash__ (self) :
        return hash (self.number)
    # end def divisors

    def __lt__ (self, other) :
        if isinstance (other, _Divisor_Dag_) :
            other = other.number
        return self.number < other
    # end def __lt__

# end class _Divisor_Dag_

if __name__ != "__main__" :
    TFL._Export ("*", "_Divisor_Dag_")
else :
    from time import time
    from _TFL.Command_Line import Command_Line
    cmd = Command_Line \
        ( option_spec =
            ( "-iterations:I=50?Number of iterations per number looked at"
            , "-limit:I=1000?Largest number to look at"
            )
        )
    iterations = cmd.iterations
    limit      = cmd.limit
    def test_time (number, iterations) :
        d                   = Divisor_Dag (number)
        table               = _Divisor_Dag_.Table.copy ()
        _Divisor_Dag_.Table = {}
        t1                  = time ()
        table               = {}
        t2                  = time ()
        ignore              = float (t2 - t1) * iterations
        t1                  = time ()
        for i in range (iterations) :
            d = Divisor_Dag (number)
            _Divisor_Dag_.Table = {}
        t2                 = time ()
        duration           = float (t2 - t1 - ignore) / iterations
        result             = duration / len (d.divisors)
        return (len (d.divisors), duration, result, number)
    cases   = ( ( 2, pyk.range (1, 16))
              , (10, [10] * 16)
              , ( 2, map (lambda i, p = primes : p [i], pyk.range (16)))
              )
    numbers = []
    for number, factors in cases :
        i = 1
        while number <= limit :
            numbers.append (number)
            number = number * factors [i]
            i      = i      + 1
    results = []
    for number in sorted (numbers) :
        results.append (test_time (number, iterations))
    for (divisors, duration, d, number) in sorted (results) :
        print \
            ( "Divisor_Dag (%8d) : %3d divisors %.6fs (%.6fs / divisor)"
            % (number, divisors, duration, d)
            )
### __END__ TFL.Divisor_Dag
