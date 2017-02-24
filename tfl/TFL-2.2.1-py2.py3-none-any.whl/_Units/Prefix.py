# -*- coding: utf-8 -*-
# Copyright (C) 2004-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Units.Prefix
#
# Purpose
#    Order of magnitude prefixes
#
# Revision Dates
#     8-Aug-2004 (CT) Creation
#    26-Nov-2014 (CT) Correct spelling of `deca` (not `deka`!)
#    ««revision-date»»···
#--



from   _TFL import TFL
import _TFL._Units

### http://en.wikipedia.org/wiki/SI_prefix

yocto  = 1E-24
zepto  = 1E-21
atto   = 1E-18
femto  = 1E-15
pico   = 1E-12
nano   = 1E-9
micro  = 1E-6
milli  = 1E-3
centi  = 1E-2
deci   = 1E-1
deca   = 1E+1
hecto  = 1E+2
kilo   = 1E+3
mega   = 1E+6
giga   = 1E+9
tera   = 1E+12
peta   = 1E+15
exa    = 1E+18
zetta  = 1E+21
yotta  = 1E+24

prefix_abbreviations = dict \
    ( y              = yocto
    , z              = zepto
    , a              = atto
    , f              = femto
    , p              = pico
    , n              = nano
    , u              = micro
    , m              = milli
    , c              = centi
    , d              = deci
    , da             = deca
    , h              = hecto
    , k              = kilo
    , M              = mega
    , G              = giga
    , T              = tera
    , P              = peta
    , E              = exa
    , Z              = zetta
    , Y              = yotta
    )

if __name__ != "__main__" :
    TFL.Units._Export \
        ( "prefix_abbreviations"
        , "yocto"
        , "zepto"
        , "atto"
        , "femto"
        , "pico"
        , "nano"
        , "micro"
        , "milli"
        , "centi"
        , "deci"
        , "deca"
        , "hecto"
        , "kilo"
        , "mega"
        , "giga"
        , "tera"
        , "peta"
        , "exa"
        , "zetta"
        , "yotta"
        )
### __END__ Prefix
