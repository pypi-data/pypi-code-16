# -*- coding: utf-8 -*-
# Copyright (C) 1999-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.subdirs
#
# Purpose
#    Get all subdirectories of a directory
#
# Revision Dates
#     3-May-1999 (CT) Creation
#    26-Jul-1999 (CT) `-exclude` and `-re_exclude` added
#    22-Dec-1999 (CT) `-separator` added
#    13-Jun-2000 (CT) Use `sos.listdir_full` instead of home-grown code
#    13-Apr-2004 (CT) Filter links from `subdirs`
#    13-Apr-2004 (CT) Output sorted
#     6-Oct-2004 (CT) `subdir_names` added
#     6-Oct-2004 (CT) `-basenames` and `-lstrip` added
#    14-Feb-2006 (CT) Moved into package `TFL`
#    16-Jun-2013 (CT) Use `TFL.CAO`, not `TFL.Command_Line`
#    ««revision-date»»···
#--

from   __future__  import print_function

from   _TFL import TFL
from   _TFL import sos

import _TFL.CAO

def subdirs (of_dir = None) :
    """Return list of all subdirectories contained in `of_dir`"""
    return \
        [ f for f in sos.listdir_full (of_dir)
            if sos.path.isdir (f) and not sos.path.islink (f)
        ]
# end def subdirs

def subdir_names (of_dir = None) :
    """Return list of the (base)-names of all subdirectories contained in
       `of_dir`.
    """
    return [sos.path.split (s) [-1] for s in subdirs (of_dir)]
# end def subdir_names

def subdirs_transitive (of_dir = None) :
    """Return transitive list of all subdirectories contained in `of_dir`."""
    result = subdirs (of_dir)
    for d in result :
        result.extend (subdirs_transitive (d))
    return result
# end def subdirs_transitive

def _main (cmd) :
    import sys
    dirs = cmd.argv or (".", )
    if cmd.newlines :
        sep = "\n"
    else :
        sep = cmd.separator
    if cmd.transitive :
        fct = subdirs_transitive
    elif cmd.basenames :
        fct = subdir_names
    else :
        fct = subdirs
    result = []
    for d in dirs :
        result.extend (fct (d))
    for exc in cmd.exclude :
        result = [r for r in result if r != exc]
    if cmd.re_exclude :
        from _TFL.Regexp import Regexp
        exc    = Regexp (cmd.re_exclude)
        result = [r for r in result if not exc.search (r)]
    if cmd.lstrip :
        result = [r.lstrip (cmd.lstrip) for r in result]
    if result :
        result.sort ()
        sys.stdout.write (sep.join (result) + "\n")
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , opts          =
        ( "-basenames:B"
              "?Print basenames of directories instead of full pathes "
              "(beware: doesn't work if -transitive is also specified)"
        , "-exclude:S #100?List of directories to exclude (space separated)"
        , "-lstrip:S?String to strip from front of directories"
        , "-newlines:B?print new lines between subdirs"
        , "-re_exclude:S?Exclude all directories matching regular expression"
        , "-separator:S= ?Separator between subdirs"
        , "-transitive:B?Print closure of subdirs"
        )
    )
if __name__ != "__main__" :
    TFL._Export ("*")
else :
    _Command ()
### __END__ TFL.subdirs
