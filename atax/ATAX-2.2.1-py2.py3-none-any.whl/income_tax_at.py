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
#    income_tax_at
#
# Purpose
#    Calculate income tax according to Austrian tax law
#
# Revision Dates
#    17-Nov-2002 (CT) Creation
#    14-Jan-2004 (CT) `2005` added
#    14-Dec-2005 (CT) Type of `amount` changed from `I` to `F`
#     3-Dec-2006 (CT) Import from `_TFL`
#    17-Sep-2007 (CT) Use `EUC_Opt_SC` and `EUC_Opt_TC` instead of home-grown
#                     code
#     8-Jan-2009 (CT) Display `raw_value` of `cmd.amount`
#     9-Jan-2009 (CT) `2009` added, display `year`
#    16-Mar-2009 (CT) `main` changed to work with `Euro` using `Decimal`
#    16-Mar-2009 (CT) `tax_brackets` for `2009` changed to final version of law
#     3-Jan-2010 (CT) Use `TFL.CAO` instead of `TFL.Command_Line`
#     7-Jan-2010 (CT) Use `TFL.CAO.Arg.EUC` instead of `TFL.CAO.Arg.Money`
#    20-May-2015 (CT) Add `2016` to `tax_brackets`
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#     9-Dec-2015 (CT) Fix `2016` of `tax_brackets`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL.Date_Time    import *
from   _TFL.EU_Currency  import *
from   _TFL.pyk          import pyk

import _TFL.CAO

year = Date ().year

def tax_brackets (year) :
    if year < 2000 :
        return \
            ( (ATS (     50000), 0.10)
            , (ATS (    100000), 0.22)
            , (ATS (    150000), 0.32)
            , (ATS (    400000), 0.42)
            , (ATS (2000000000), 0.50)
            )
    elif year < 2002 :
        return \
            ( (ATS (     50000), 0.00)
            , (ATS (     50000), 0.21)
            , (ATS (    200000), 0.31)
            , (ATS (    400000), 0.41)
            , (ATS (2000000000), 0.50)
            )
    elif year < 2005 :
        return \
            ( (EUR (      3640), 0.00)
            , (EUR (      3630), 0.21)
            , (EUR (     14530), 0.31)
            , (EUR (     29070), 0.41)
            , (EUR (2000000000), 0.50)
            )
    elif year < 2009 :
        return \
            ( (EUR (     10000), 0.00)
            , (EUR (     15000), 0.3833)
            , (EUR (     26000), 0.436)
            , (EUR (2000000000), 0.50)
            )
    elif year < 2016 :
        return \
            ( (EUR (     11000), 0.000)
            , (EUR (     14000), 0.3635)
            , (EUR (     35000), 0.4321429)
            , (EUR (2000000000), 0.500)
            )
    else :
        return \
            ( (EUR (     11000), 0.000)
            , (EUR (      7000), 0.250)
            , (EUR (     13000), 0.350)
            , (EUR (     29000), 0.420)
            , (EUR (     30000), 0.480)
            , (EUR (    910000), 0.500)
            , (EUR (2000000000), 0.550) ### as of 2015, applies up to 2020
            )
# end def tax_brackets

def tax (amount, year = year) :
    result     = 0
    brackets   = tax_brackets (year)
    remains    = amount
    tax_chunks = []
    for chunk, rate in brackets :
        if remains <= 0.0 :
            break
        if chunk > remains :
            chunk = remains
        ### don't use `-=` here (or `chunk = remains` fails)
        remains  = remains - chunk
        tc       = chunk   * rate
        result  += tc
        tax_chunks.append ((chunk, rate, tc))
    return result, tax_chunks
# end def tax

def _main (cmd) :
    source_currency        = cmd.source_currency
    year                   = cmd.year
    amount                 = cmd.amount
    tax_amount, tax_chunks = tax (amount, year)
    if cmd.verbose :
        for c, r, t in tax_chunks :
            print \
                ( "%2d%% for %14s : %14s"
                % (r * 100, c.as_string_s (), t.as_string_s ())
                )
    f = ( "In %s, for a taxable income of %s [%s]\n"
          "    you pay a tax of %s (%5.2f%%) and get %s\n"
        )
    print \
        ( f
        % ( year, amount, cmd ["amount:raw"], tax_amount
          , (tax_amount / (amount / 100.0)).amount
          , amount - tax_amount
          )
        )
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , args        =
        ( TFL.CAO.Arg.EUC
            ( name        = "amount"
            , description = "Amount of taxable income"
            )
        ,
        )
    , min_args    = 1
    , max_args    = 1
    , opts        =
        ( "-verbose:B?Show chunks, too"
        , "-year:I=%s?Year of interest" % (year, )
        , TFL.CAO.Opt.EUC_Source ()
        , TFL.CAO.Opt.EUC_Target ()
        )
    , description = "Calculate income tax for `year`"
    )

if __name__ == "__main__" :
    _Command ()
### __END__ ATAX.income_tax_at
