# -*- coding: utf-8 -*-
# Copyright (C) 2012 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.Werkzeug.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.Werkzeug.Profiler
#
# Purpose
#    Profiler for werkzeug-based WSGI applications
#
# Revision Dates
#    20-Jun-2012 (CT) Factor from `GTW.Werkzeug.Application`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                      import GTW
from   _TFL                      import TFL

import _GTW._Werkzeug

import _TFL._Meta.Object

from   werkzeug.contrib.profiler import ProfilerMiddleware, MergeStream

import os, sys

class Profiler (TFL.Meta.Object) :
    """Profiler for werkzeug-based WSGI applications."""

    def __init__ \
            ( self
            , delete_logs  = False
            , log_files    = ()
            , restrictions = ()
            , sort_by      = ('time', 'calls')
            ) :
        self.delete_logs   = delete_logs
        self.log_files     = log_files
        self.restrictions  = restrictions
        self.sort_by       = sort_by
    # end def __init__

    def __call__ (self, app) :
        file_handles = []
        for fn in self.log_files :
            if hasattr (fn, "write") :
                file_handles.append (fn)
            elif fn == "stderr" :
                file_handles.append (sys.stderr)
            else :
                if self.delete_logs and os.path.isfile (fn) :
                    os.unlink (fn)
                file_handles.append (open (fn, "w"))
        stream = MergeStream (* file_handles) if file_handles else None
        return ProfilerMiddleware (app, stream, self.sort_by, self.restrictions)
    # end def __call__

# end class Profiler

if __name__ != "__main__" :
    GTW.Werkzeug._Export ("*")
### __END__ GTW.Werkzeug.Profiler
