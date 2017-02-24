# -*- coding: utf-8 -*-
# Copyright (C) 2008-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package ATAX.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    ATAX.fahrtenbuch
#
# Purpose
#    Fahrtenbuch
#
# Revision Dates
#     4-Jan-2008 (CT) Creation (ported from a perl version)
#     5-Jan-2008 (CT) Use `CAL.Date_Time` instead of (obsolete) `TFL.Date_Time`
#     9-Jul-2009 (MG) Support for `km_geld` added
#     5-Aug-2009 (CT) `km_business`, `km_private`, and `private_percent`
#                     factored (in class `Fahrtenbuch`)
#     3-Jan-2010 (CT) Use `TFL.CAO` instead of `TFL.Command_Line`
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    31-Oct-2015 (CT) Add `@pyk.adapt__str__` to `FB_Entry`
#    28-Dec-2015 (CT) Fix `__str__` (use `pyk.text_type`, not `str`)
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _ATAX             import ATAX
from   _CAL              import CAL
from   _TFL              import TFL

from   _ATAX.accounting  import ignor_pat

from   _TFL.predicate    import *
from   _TFL.pyk          import pyk
from   _TFL.Regexp       import *
from   _TFL._Meta.Once_Property import Once_Property

import _CAL.Date_Time

import _TFL._Meta.Object
import _TFL.CAO
import _TFL.Environment

@pyk.adapt__bool__
@pyk.adapt__str__
class FB_Entry (TFL.Meta.Object) :
    """Model one entry of a Fahrtenbuch"""

    str_format  = r"  %-11s & %8d & %6d & %s"
    tex_format  = r"  %-10s & %6d & %6d & %4d & %4d & \sf %s"
    atax_format = \
        " %s  & & & %6.2f & b & 7500 & 2100 & -  & e & & KM Geld (%5.1f km)"

    def __init__ (self, date, km_start, km_finis, priv, desc, ** kw) :
        self.date     = date
        self.km_start = float (km_start)
        self.km_finis = float (km_finis)
        self.priv     = float (priv or 0)
        self.desc, _, self.comment = (x.strip () for x in split_hst (desc, "%"))
        self.__dict__.update (kw)
    # end def __init__

    @Once_Property
    def delta (self) :
        return self.km_finis - self.km_start
    # end def delta

    @Once_Property
    def km_business (self) :
        return self.delta * (1.0 - self.priv / 100.)
    # end def km_business

    @Once_Property
    def km_private (self) :
        return self.delta * (self.priv / 100.)
    # end def km_private

    def tex (self) :
        date    = self.date.formatted ("%d.%m.%Y")
        bus_km  = self.km_business
        priv_km = self.km_private
        desc    = self.desc ### TeX-quote `desc`
        return self.tex_format % \
            (date, self.km_start, self.km_finis, bus_km, priv_km, desc)
    # end def tex

    def atax (self) :
        date    = self.date.formatted ("%d.%m")
        km      = self.km_business
        f       = 0.42 ### 0.42 Euro/km
        if self.date < CAL.Date_Time (2008, 7, 1) :
            f   = 0.38
        return self.atax_format % (date, f * km, km)
    # end def atax

    def __bool__ (self) :
        return bool (self.delta)
    # end def __bool__

    def __str__ (self) :
        date = self.date.formatted ("%d.%m.%Y")
        return self.str_format % (date, self.km_finis, self.priv, self.desc)
    # end def __str__

# end class FB_Entry

class Fahrtenbuch (TFL.Meta.Object) :
    """Model a Fahrtenbuch"""

    lines_per_page = 50
    Entry          = FB_Entry

    def __init__ (self, user, entries = []) :
        self.user    = user
        self.entries = []
        for e in entries :
            self.add (e)
    # end def __init__

    def add (self, entry) :
        self.entries.append (entry)
    # end def add

    @classmethod
    def from_file (cls, user, file_name) :
        result = cls (user)
        add    = result.add
        last   = None
        with open (file_name, "rb") as file :
            for l in result._read_lines (file) :
                line = pyk.decoded (l, "utf-8", "iso-8859-1")
                try :
                    d, km, priv, desc = \
                        [f.strip () for f in line.split ("&", 4)]
                except ValueError :
                    pyk.fprint ("Split error `%s`" % line)
                else :
                    last = result._new_entry (last, d, km, priv, desc)
                    add (last)
        return result
    # end def from_file

    @property
    def km_business (self) :
        return sum (e.km_business for e in self.entries)
    # end def km_business

    def km_geld (self) :
        result = ["""$source_currency = "EUR";"""]
        for e in self.entries :
            if e.km_business :
                result.append (e.atax ())
        return "\n".join (result)
    # end def km_geld

    @property
    def km_private (self) :
        return sum (e.km_private for e in self.entries)
    # end def km_private

    @property
    def private_percent (self) :
        kmb    = self.km_business
        kmp    = self.km_private
        result = 0
        if kmp :
            result = 100.0 / ((kmb + kmp) / kmp)
        return result
    # end def private_percent

    def tex (self) :
        result  = []
        entries = self.entries
        if entries :
            head    = entries [0]
            tail    = entries [-1]
            h_date  = head.date.formatted ("%m/%Y")
            t_date  = tail.date.formatted ("%m/%Y")
            dates   = h_date
            if h_date != t_date :
                dates = "%s -- %s" % (h_date, t_date)
            add    = result.append
            add ( ( r"\def\fahrtenbuchpageheader"
                    r"{\begin{Larger}\bf "
                    r"\strut\triline{Fahrtenbuch}{%s}{%s}"
                    r"\end{Larger}"
                    r"\par\vspace{0.0cm}"
                    r"}"
                  )
                % (self.user, dates)
                )
            add (r"\begin{fahrtenbuch}")
            i   = 1
            lpp = self.lines_per_page
            for e in entries :
                if e :
                    sep = [r"\\ ", r"\CR"] [(i % 5) == 0]
                    add ("%s %s" % (e.tex (), sep.strip ()))
                    i += 1
                    if i > lpp :
                        add (r"\end{fahrtenbuch}")
                        add (r"\\ \hbox{\strut}\hfill ./..%")
                        add (r"\begin{fahrtenbuch}")
                        i = 1
            add (r"\hline\hline")
            kmb  = self.km_business
            kmp  = self.km_private
            priv = self.private_percent
            add ( FB_Entry.tex_format
                % ( "Total", head.km_start, tail.km_finis, kmb, kmp
                  , r"\hfill Privatanteil = \percent{%5.2f} \CR" % priv
                  )
                )
            add (r"\end{fahrtenbuch}")
        return "\n".join (result)
    # end def tex

    def _new_entry (self, last, d, km_finis, priv, desc) :
        km_start = km_finis
        if last is not None :
            km_start = last.km_finis
        return self.Entry \
            (CAL.Date_Time.from_string (d), km_start, km_finis, priv, desc)
    # end def _new_entry

    def _read_lines (self, file) :
        for l in file :
            line = pyk.decoded (l.strip (), "utf-8", "iso-8859-1")
            if line and not ignor_pat.match (line) :
                yield line
    # end def _read_lines

    def __str__ (self) :
        return "\n".join (pyk.text_type (e) for e in self.entries)
    # end def __str__

# end class Fahrtenbuch

def _main (cmd) :
    ATAX.Command.load_config (cmd)
    fb = Fahrtenbuch.from_file (cmd.user, cmd.fahrtenbuch)
    if not cmd.km_geld :
        pyk.fprint (fb.tex ())
    else :
        pyk.fprint (fb.km_geld ())
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , args        =
        ("fahrtenbuch:P?File defining fahrtenbuch", )
    , min_args    = 1
    , max_args    = 1
    , opts        =
        ( "Config:P,?Config file(s)"
        , "user:S=%s" % TFL.Environment.username.capitalize ()
        , "km_geld:B?Print the factoring for the KM Geld"
        , TFL.CAO.Opt.Output_Encoding (default = "iso-8859-15")
        )
    )

if __name__ != "__main__" :
    ATAX._Export ("*")
else :
    _Command ()
### __END__ ATAX.fahrtenbuch
