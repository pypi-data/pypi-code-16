# -*- coding: utf-8 -*-
# Copyright (C) 1999-2015 Mag. Christian Tanzer. All rights reserved
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
#    umsatzsteuer
#
# Purpose
#    Calculate monthly VAT for the austrian finance ministry
#
# Revision Dates
#    14-Jan-1999 (CT) Creation
#     7-Feb-1999 (CT) Special handling for `source_currency' added to
#                     `code_pat' processing
#    26-Feb-1999 (CT) `help_on_err = 1' passed to Command_Line
#     4-Mar-1999 (CT) Handling of `privat' added
#     3-Jan-2000 (CT) Logic of `umsatzsteuer' factored into
#                     `V_Account.add_lines'
#    26-Dec-2001 (CT) Access to cmd-options simplified
#    26-Dec-2001 (CT) Function `umsatzsteuer` moved to `accounting`
#     6-Jan-2003 (CT) Alias `umsatzsteuer` for `add_account_file` added
#    19-Feb-2006 (CT) Import from package _ATAX
#    15-May-2006 (CT) Call to `finish` added
#    11-Feb-2007 (CT) `string` functions replaced by `str` methods
#    17-Sep-2007 (CT) Modernized
#    17-Sep-2007 (CT) Use `Account.add_file`
#    17-Sep-2007 (CT) `main` refactored
#     3-Jan-2010 (CT) Use `TFL.CAO` instead of `TFL.Command_Line`
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from _ATAX.accounting import *

sep_1000 = { "." : ",", "," : "."}

class Ust_Command (Command) :

    def _add_files (self, cmd, account, categories, source_currency) :
        self.__super._add_files (cmd, account, categories, source_currency)
        account.finish ()
    # end def _add_files

    def _create_account (self, cmd, categories, source_currency, vst_korrektur) :
        if cmd.online_format :
            EUC.target_currency.decimal_sign = ","
            EUC.target_currency.sep_1000     = ""
        else :
            EUC.target_currency.decimal_sign = cmd.decimal_sign
            EUC.target_currency.sep_1000     = sep_1000 [cmd.decimal_sign]
        return V_Account (vst_korrektur = vst_korrektur)
    # end def _create_account

    def _output (self, cmd, account, categories, source_currency) :
        if cmd.online_format :
            account.print_summary_online ()
        else :
            if not cmd.summary :
                account.print_entries ("\f")
                if cmd.reverse :
                    account.print_entries_by_group ("\f")
            account.print_summary ()
    # end def _output

    def _opt_spec (self) :
        return self.__super._opt_spec () + \
            ( "-decimal_sign:S=."
            , "-online_format:B?Format for cope/paste into online form"
            , "-reverse:B"
            , "-summary:B"
            )
    # end def _opt_spec

Command = Ust_Command # end class Ust_Command

if __name__ == "__main__":
    Ust_Command ()
### __END__ ATAX.umsatzsteuer
