# -*- coding: utf-8 -*-
# Copyright (C) 2002-2015 Mag. Christian Tanzer. All rights reserved
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
#    anlagenverzeichnis
#
# Purpose
#    Manage depreciations (as required by Austrian tax law)
#
# Revision Dates
#    12-Feb-2002 (CT) Creation (rewrite of perl code)
#    19-Jan-2003 (CT) Rest value made dependent on target_currency, instead
#                     of source_currency
#    19-Jan-2003 (CT) `-Start_year` added
#    19-Jan-2003 (CT) Don't show entries totally depreciated
#    22-Dec-2003 (CT) `Anlagen_Entry.evaluate` changed to not add
#                     non-contemporary entries to totals
#    19-Feb-2006 (CT) Import from packages _ATAX and _TFL
#    11-Feb-2007 (CT) `string` functions replaced by `str` methods
#    17-Sep-2007 (CT) Use `EUC_Opt_SC` and `EUC_Opt_TC` instead of home-grown
#                     code
#     5-Feb-2008 (CT) Support for `FBiG` added
#    18-Feb-2008 (CT) s/_Base/_Base_/g
#    18-Feb-2008 (CT) `_IFB_`, `IFB`, and `FBiG` factored
#    12-Aug-2008 (CT) `p_konto` added
#    13-Aug-2008 (CT) `_write_entry` changed to only write `e.ifb.value` if
#                     `ifb` is still alive (and output formatting corrected)
#    11-Mar-2009 (CT)  Check `target_currency.to_euro_factor == 1.0` instead
#                      of comparing `target_currency` to `EU_Currency`
#    27-Mar-2009 (CT) `active` factored (and changed to allow entries with
#                     `base_rate == 0`)
#    27-Mar-2009 (CT) `account_format` and `_update_account_entry` changed to
#                     allow line-specific date (for `Abgang`)
#     3-Jan-2010 (CT) Use `TFL.CAO` instead of `TFL.Command_Line`
#     7-Feb-2011 (CT) `cat` and `total_per_cat` added
#     7-Jun-2012 (CT) Use `TFL.r_eval`
#     3-Jan-2014 (CT) Add `output_encoding`; use `pyk.fprint`, not `print`
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    ««revision-date»»···
#--

from   __future__       import division, print_function
from   __future__       import absolute_import, unicode_literals

from   _ATAX.accounting import *
from   _ATAX.accounting import _Base_, _Entry_

from   _TFL.pyk         import pyk
from   _TFL.Regexp      import *

import _TFL.CAO
import _TFL.r_eval

class _Mixin_ (TFL.Meta.Object) :

    def _setup_dates (self, target_year) :
        self.head_date       = "1.1.%s"   % (target_year, )
        self.midd_date       = "30.6.%s"  % (target_year, )
        self.tail_date       = "31.12.%s" % (target_year, )
        self.head_time       = Date (self.head_date)
        self.midd_time       = Date (self.midd_date)
        self.tail_time       = Date (self.tail_date)
        self.target_year     = int  (target_year)
    # end def _setup_dates

# end class _Mixin_

@pyk.adapt__bool__
class _IFB_ (TFL.Meta.Object) :
    """Base class for FBiG and IFB."""

    def __init__ (self, entry) :
        self.entry  = entry
        self.alive  = entry.birth_time.year + 4 >  entry.target_year
        self.is_new = entry.birth_time.year     == entry.target_year
    # end def __init__

    def round (self) :
        self.value  = self.value.rounded_as_target ()
    # end def round

    def __bool__ (self) :
        return self.alive and bool (self.value)
    # end def __bool__

# end class _IFB_

class FBiG (_IFB_) :
    """Model a FBiG (Freibetrag für investierte Gewinne)."""

    abbr    = "FBiG"
    account = None
    name    = "Freibetrag für investierte Gewinne"

    def __init__ (self, entry, ifb, source_currency) :
        self.__super.__init__ (entry)
        self.value = source_currency (float (ifb or entry.birth_value))
    # end def __init__

# end class FBiG

class IFB (_IFB_) :
    """Model a IFB (Investitionsfreibetrag)."""

    abbr    = "IFB"
    account = 7802
    name    = "Investitionsfreibetrag"

    def __init__ (self, entry, ifb, source_currency) :
        self.__super.__init__ (entry)
        self.rate  = int (ifb or 0) / 100.0
        self.value = entry.birth_value * self.rate
    # end def __init__

# end class IFB

class Anlagen_Entry (_Mixin_, _Entry_) :

    cat            = "Normal"
    rate_pattern   = r"(?P<rate> [-+*/().0-9\s]+)"
    first_rate_pat = Regexp (rate_pattern, re.X)
    later_rate_pat = Regexp \
        ( r"(?P<year> \d\d (?: \d\d)?) \s* : \s* " + rate_pattern
        , re.X
        )
    _cat_pat       = Regexp (r"C\[(?P<cat> [^]]+)\]", re.VERBOSE)

    def __init__ (self, line, anlagenverzeichnis) :
        try :
            ( self.desc, self.supplier, self.flags
            , self.birth_date, self.a_value, self.afa_spec, ifb
            , self.death_date
            )                = split_pat.split     (line, 8)
        except ValueError as exc :
            print (line)
            raise
        final                = "31.12.2037"
        self.p_konto         = self._get_p_konto (self.flags)
        self.birth_time      = Date (self.birth_date)
        self.death_time      = Date (self.death_date or final)
        self.alive           = self.death_time > anlagenverzeichnis.tail_time
        self.contemporary    = \
            (   self.birth_time <= anlagenverzeichnis.tail_time
            and self.death_time >= anlagenverzeichnis.head_time
            )
        if int (self.death_time.year) < int (anlagenverzeichnis.year) :
            self._setup_dates (self.death_time.year)
        else :
            self._setup_dates (anlagenverzeichnis.year)
        self.half_date       = "1.7.%s" % (self.birth_time.year, )
        if "~" in self.flags :
            self.half_date   = "1.1.%s" % (self.birth_time.year + 1, )
        self.half_time       = Date (self.half_date)
        self.desc            = desc_strip_pat.sub  ("", self.desc)
        currency_match       = currency_pat.search (self.a_value)
        a_value              = self.a_value
        source_currency      = anlagenverzeichnis.source_currency
        if currency_match :
            source_currency  = EU_Currency.Table   [currency_match.group (1)]
            a_value          = currency_pat.sub    ("", a_value)
        if EUC.target_currency is not ATS :
            self.zero        = source_currency     (0.0)
        else :
            self.zero        = source_currency     (1.0)
        self.source_currency = source_currency
        self.birth_value     = source_currency     (TFL.r_eval (a_value))
        self.new_value       = source_currency     (0.0)
        self.out_value       = source_currency     (0.0)
        if "G" in self.flags :
            self.ifb         = FBiG (self, ifb, source_currency)
        else :
            self.ifb         = IFB  (self, ifb, source_currency)
        self._set_cat (self.flags)
    # end def __init__

    @property
    def active (self) :
        return \
            (   self.contemporary
            and (self.current_depreciation > 0 or self.base_rate == 0)
            )
    # end def active

    def evaluate (self) :
        self._calc_rates ()
        self.current_depreciation = \
            self.birth_value * (self.current_rate / 100.0)
        if "=" not in self.flags :
            self.head_value = max \
                ( self.birth_value * ((100.0 - self.past_total_rate) / 100.)
                , self.zero
                )
            self.tail_value = self.head_value - self.current_depreciation
            if self.tail_value < self.zero :
                self.tail_value = self.zero
                self.current_depreciation -= self.zero
        else :
            self.head_value = self.tail_value = self.birth_value
        if self.birth_time >= self.head_time :
            self.head_value = self.source_currency (0.0)
            self.new_value  = self.birth_value
        if not self.alive :
            self.out_value  = self.tail_value
            self.tail_value = self.source_currency (0.0)
        if self.tail_value.target_currency.to_euro_factor != 1.0 :
            self.birth_value          = self.birth_value.rounded_as_target ()
            self.head_value           = self.head_value.rounded_as_target  ()
            self.tail_value           = self.tail_value.rounded_as_target  ()
            self.new_value            = self.new_value.rounded_as_target   ()
            self.out_value            = self.out_value.rounded_as_target   ()
            self.current_depreciation = \
                self.current_depreciation.rounded_as_target ()
            if self.ifb :
                self.ifb.round ()
    # end def evaluate

    def _calc_rates (self) :
        rates          = [x.strip () for x in self.afa_spec.split (",")]
        first_rate     = rates [0]
        first_rate_pat = self.first_rate_pat
        later_rate_pat = self.later_rate_pat
        if not first_rate_pat.match (first_rate) :
            raise ValueError \
                ("%s doesn't match a depreciation rate" % (first_rate, ))
        later_rates = []
        for r in rates [1:] :
            if not later_rate_pat.match (r) :
                raise ValueError \
                    ("%s doesn't match a depreciation rate" % (r, ))
            y = Time_Tuple (later_rate_pat.year).year
            later_rates.append ((y, TFL.r_eval (later_rate_pat.rate) * 1.0))
        y_rate  = self.base_rate = TFL.r_eval (first_rate_pat.rate) * 1.0
        if later_rates :
            later_rates.append ((self.target_year, later_rates [-1] [1]))
        else :
            later_rates.append ((self.target_year, y_rate))
        y_rates = self.y_rates   = \
            [y_rate * ((0.5, 1.0) [self.birth_time < self.half_time])]
        if self.birth_time < self.head_time :
            current_year = self.birth_time.year + 1
            for target_year, next_rate in later_rates :
                while current_year < target_year :
                    y_rates.append (y_rate)
                    current_year += 1
                y_rate = self.base_rate = next_rate
            y_rates.append \
                (y_rate * ((0.5, 1.0) [self.midd_time < self.death_time]))
        self.current_rate     = y_rates [-1]
        past_total_rate       = 0
        for y_rate in y_rates [:-1] :
            past_total_rate  += y_rate
        self.past_total_rate  = min (past_total_rate, 100.0)
        if self.past_total_rate + self.current_rate > 100.0 :
            self.current_rate = 100.0 - self.past_total_rate
    # end def _calc_rates

    def _set_cat (self, flags) :
        pat = self._cat_pat
        if pat.search (flags) :
            self.cat = pat.cat
    # end def _set_cat

# end class Anlagen_Entry

class Anlagenverzeichnis (_Mixin_, _Base_) :

    assignment_pat = Regexp \
        ( r"^\$ "
          r"(?P<var> account_file | source_currency)"
          r"\s* = \s*"
          r"(?P<value> .*)"
          r"\s* ;"
        , re.X
        )

    header_format  = "%-48s  %-8s  %10s  %10s  %8s  %10s  %10s"
    entry1_format  = "%-44s%4s  %8s  %10.2f  %10.2f     %5.2f  %10.2f  %10.2f"
    newifb_format  = "  %-46s  %8s  %10s  %10s  %8s  %10.2f  %10s"
    alive_format   = "  %-46s  %8s  %10s  %10s  %8s"
    dying_format   = "  %-36.31s%10s  %8s  %10s  %10s  %8s  %10.2f  %10s"
    footer_format  = "\n%-48s  %8s  %10.2f  %10.2f  %8s  %10.2f  %10.2f"
    new_format     = "%-48s  %8s  %10s  %10.2f"
    out_format     = "%-48s  %8s  %10s  %10s  %8s  %10.2f"

    account_format = \
        " %s & & & %10.2f & b & %-5s & 2100 & - & %-3s & & %-6s %s\n"


    ifb_type       = ""

    def __init__ (self, year, start_year, file_name, source_currency, account_file = None) :
        self.year               = year
        self.start_time         = Date ("1.1.%s" % (start_year, ))
        self.file_name          = file_name
        self.source_currency    = source_currency
        self.account_file       = account_file
        self.entries            = []
        self.total_birth_value  = source_currency (0.0)
        self.total_head_value   = source_currency (0.0)
        self.total_tail_value   = source_currency (0.0)
        self.total_new_value    = source_currency (0.0)
        self.total_out_value    = source_currency (0.0)
        self.total_ifb_value    = source_currency (0.0)
        self.total_depreciation = source_currency (0.0)
        self.total_per_cat      = defaultdict     (EUR)
        self._setup_dates (year)
        self.add_file     (file_name)
    # end def __init__

    def add_file (self, file_name) :
        assignment_pat = self.assignment_pat
        file           = open (file_name, "rb")
        for line in file :
            line                      = self._decoded (line)
            if ignor_pat.match (line) : continue
            line                      = ws_head_pat.sub ("", line, count = 1)
            line                      = ws_tail_pat.sub ("", line, count = 1)
            if not line               : continue
            if assignment_pat.match (line) :
                self.eval_line (line, assignment_pat)
            else :
                self.add_line  (line)
        file.close ()
    # end def add_file

    def eval_line (self, line, match) :
        name       = match.var
        expression = match.value.replace \
                         ("$target_year", str (self.target_year))
        value      = TFL.r_eval (expression)
        if name == "source_currency" :
            value  = EUC.Table [value]
        setattr (self, name, value)
    # end def eval_line

    def add_line (self, line) :
        self.entries.append (Anlagen_Entry (line, self))
    # end def add_line

    def evaluate (self) :
        for e in self.entries :
            if (not e.contemporary) or e.birth_time < self.start_time :
                e.contemporary = 0
                continue
            e.evaluate ()
            if e.active :
                self.total_birth_value     += e.birth_value
                self.total_head_value      += e.head_value
                self.total_tail_value      += e.tail_value
                self.total_new_value       += e.new_value
                self.total_out_value       += e.out_value
                self.total_depreciation    += e.current_depreciation
                self.total_per_cat [e.cat] += e.current_depreciation
            if e.ifb and e.ifb.is_new :
                self.ifb_type               = e.ifb.__class__
                self.total_ifb_value       += e.ifb.value
    # end def evaluate

    def write (self) :
        pyk.fprint \
            ( self.header_format
            % ( "", "", "Anschaff/", "Buchwert", " Afa ", "Afa", "Buchwert")
            )
        pyk.fprint \
            ( self.header_format
            % ( "Text", "Datum", "Teil-Wert", "1.1.", "  %  "
              , "IFB/Abgang", "31.12."
              )
            )
        pyk.fprint ("\n%s\n" % ("=" * 116, ))
        for e in self.entries :
            if e.active :
                self._write_entry (e)
        pyk.fprint ("\n%s\n" % ("=" * 116, ))
        pyk.fprint \
            ( self.footer_format
            % ( "Summe", ""
              , self.total_birth_value
              , self.total_head_value
              , "Afa"
              , self.total_depreciation
              , self.total_tail_value
              )
            )
        if len (self.total_per_cat) > 1 :
            for k, v in sorted (pyk.iteritems (self.total_per_cat)) :
                pyk.fprint ((self.out_format % ("", "", "", "", k, v)))
        pyk.fprint \
            (self.new_format % ("Neuzugänge", "", "", self.total_new_value))
        pyk.fprint \
            ( self.out_format
            % ("Abgänge", "", "", "", "", self.total_out_value)
            )
        if self.total_ifb_value :
            pyk.fprint \
                ( self.out_format
                % ( self.ifb_type.name, "", "", "", self.ifb_type.abbr
                  , self.total_ifb_value
                  )
                )
    # end def write

    def _write_entry (self, e) :
        ifb_indicator = ""
        if e.ifb :
            ifb_indicator = e.ifb.abbr
        pyk.fprint \
            ( self.entry1_format
            % ( e.desc
              , ifb_indicator
              , e.birth_time.formatted ("%d.%m.%y")
              , e.birth_value
              , e.head_value
              , e.base_rate
              , e.current_depreciation
              , e.tail_value
              )
            )
        if e.alive :
            if e.ifb and e.ifb.is_new :
                pyk.fprint \
                    ( self.newifb_format
                    % ( e.supplier, "", "", "", e.ifb.abbr, e.ifb.value, "")
                    )
            elif e.ifb :
                pyk.fprint ("  %-36s%10.2f" % (e.supplier, e.ifb.value))
            else :
                pyk.fprint \
                    ( self.alive_format
                    % (e.supplier, "", "", "", ("", "ewig") ["=" in e.flags])
                    )
        else :
            pyk.fprint \
                ( self.dying_format
                % ( e.supplier
                  , "Abgang"
                  , e.death_time.formatted ("%d.%m.%y")
                  , ifb_indicator
                  , ("", e.ifb.value.as_string_s ()) [bool (e.ifb)]
                  , ("", "ewig") ["=" in e.flags]
                  , e.out_value
                  , ""
                  )
                )
    # end def _write_entry

    def update_accounts (self) :
        if self.account_file :
            file = open (self.account_file, "w")
        else :
            file = sys.stdout
        for e in self.entries :
            if e.contemporary :
                self._update_account_entry (e, file)
        if self.account_file :
            file.close ()
    # end def update_accounts

    def _update_account_entry (self, e, file) :
        cat = "fe"
        if e.p_konto :
            cat = "%sP[%s]" % (cat, e.p_konto)
        eoy = Date (day_to_time_tuple  ("31.12."))
        if e.active and e.current_depreciation :
            self._write \
                ( file
                , self.account_format
                % ( eoy.formatted ("%d.%m.")
                  , e.current_depreciation, 7800, cat, "Afa",      e.desc
                  )
                )
        if e.ifb and e.ifb.is_new and e.ifb.account :
            self._write \
                ( file
                , self.account_format
                % (eoy.formatted ("%d.%m.")
                  , e.ifb.value, e.ifb.account, cat, e.ifb.abbr, e.desc
                  )
                )
        if not e.alive :
            self._write \
                ( file
                , self.account_format
                % ( e.death_time.formatted ("%d.%m.")
                  , e.out_value, 7801, cat, "Abgang",   e.desc
                  )
                )
    # end def _update_account_entry

    def _write (self, file, s) :
        file.write (pyk.as_str (s))
    # end def _write


# end class Anlagenverzeichnis

def _main (cmd) :
    source_currency     = cmd.source_currency
    year                = cmd.year
    start               = cmd.Start_year
    file_name           = cmd.anlagenverzeichnis
    account_file        = cmd.account_file
    anlagenverzeichnis  = Anlagenverzeichnis \
        (year, start, file_name, source_currency, account_file)
    anlagenverzeichnis.evaluate ()
    anlagenverzeichnis.write    ()
    if cmd.update_accounts :
        anlagenverzeichnis.update_accounts ()
    return anlagenverzeichnis
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , args        =
        ( "year:S?Year of interest"
        , "anlagenverzeichnis:P?File defining depreciation data"
        )
    , min_args    = 2
    , max_args    = 2
    , opts        =
        ( "-account_file:P?Name of account file to update"
        , "-Start_year:S=1988?Skip all entries before `Start_year`"
        , "-update_accounts:B?Add depreciation entries to account file"
        , TFL.CAO.Arg.EUC_Source ()
        , TFL.CAO.Arg.EUC_Target ()
        , TFL.CAO.Opt.Output_Encoding (default = "utf-8")
        )
    , description = "Calculate depreciations for `year`"
    )

"""
year=2007 ; python -m ATAX.anlagenverzeichnis $year ~/EAR/anlagen_gewerbe.dat
"""
if __name__ == "__main__":
    _Command ()
### __END__ ATAX.anlagenverzeichnis
