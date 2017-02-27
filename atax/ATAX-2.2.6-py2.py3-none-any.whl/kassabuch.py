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
#    kassabuch
#
# Purpose
#    Write kassabuch file for a month
#
# Revision Dates
#     9-Feb-1999 (CT) Creation
#     6-Feb-2000 (CT) `vst_korrektur' passed to `V_Account' instead of to
#                     `umsatzsteuer'
#     5-Jul-2006 (CT) Import from `_ATAX`
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

from   _TFL.pyk          import pyk

from _ATAX.accounting    import *

par_sub_pat = re.compile ("\(([^)]+)\)")

def kassabuch (account, file) :
    """Write entries in `account' to kassabuch `file'"""
    for e in account.entries :
        if not isinstance (e, Account_Entry) :
            continue
        e.desc = par_sub_pat.sub ("[\\1]", e.desc)
        if "-" in e.dir :
            file.write \
                ( pyk.encoded
                    ( "\\A %6s %-50s (%8s) [%s]\n"
                    % (e.date, e.desc, e.gross.as_string (), e.number)
                    )
                )
        elif "+" in e.dir :
            print ("Income entries not yet implemented", e)
# end def kassabuch

class Command (Command) :

    def _create_account (self, cmd, categories, source_currency, vst_korrektur) :
        return V_Account (vst_korrektur = vst_korrektur)
    # end def _create_account

    def _output (self, cmd, account, categories, source_currency) :
        if cmd.output :
            file = open (cmd.output, "wb")
        else :
            file = sys.stdout
        kassabuch (account, file)
    # end def _output

    def _opt_spec (self) :
        return self.__super._opt_spec () + ("-output:S", )
    # end def _opt_spec

# end class Command

if __name__ == "__main__":
    Command ()
### __END__ ATAX.kassabuch
