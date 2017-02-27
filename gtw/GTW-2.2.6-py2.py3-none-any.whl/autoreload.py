# -*- coding: utf-8 -*-
# Copyright (C) 2007-2010 Martin Glück. All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.autoreload
#
# Purpose
#    Autoreload python modules
#
# Revision Dates
#    12-Sep-2009 (MG) Creation
#    ««revision-date»»···
#--

# Borrowed from Django (www.djangoproject.com)
# Autoreloading launcher.
# Borrowed from Peter Hunt and the CherryPy project (http://www.cherrypy.org).
# Some taken from Ian Bicking's Paste (http://pythonpaste.org/).
#
# Portions Copyright (C) 2004-2010, CherryPy Team (team@cherrypy.org)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of the CherryPy Team nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os, sys, time

import thread

# This import does nothing, but it's necessary to avoid some race conditions
# in the threading module. See http://code.djangoproject.com/ticket/2330 .
try:
    import threading
except ImportError:
    pass

RUN_RELOADER = True

_mtimes = {}
_win    = sys.platform == "win32"

def code_changed () :
    global _mtimes, _win
    for filename in ( fn for fn in
                        (    getattr (m, "__file__", None)
                         for m in sys.modules.values () ## can't use iter here
                        )
                      if fn
                    ) :
        if filename.endswith (".pyc") or filename.endswith (".pyo") :
            filename = filename[:-1]
        if not os.path.exists (filename) :
            continue # File might be in an egg, so it can't be reloaded.
        stat  = os.stat (filename)
        mtime = stat.st_mtime
        if _win:
            mtime -= stat.st_ctime
        if filename not in _mtimes :
            _mtimes[filename] = mtime
            continue
        if mtime != _mtimes [filename] :
            _mtimes = {}
            return True
    return False
# end def code_changed

def reloader_thread () :
    while RUN_RELOADER:
        if code_changed () :
            sys.exit    (3) # force reload
        time.sleep      (1)
# end def reloader_thread

def restart_with_reloader () :
    while True :
        args = [sys.executable] + sys.argv
        if sys.platform == "win32" :
            args = ['"%s"' % arg for arg in args]
        new_environ = os.environ.copy()
        new_environ ["RUN_MAIN"] = "true"
        exit_code = os.spawnve (os.P_WAIT, sys.executable, args, new_environ)
        if exit_code != 3 :
            return exit_code
# end def restart_with_reloader

def python_reloader (main_func, args, kwargs) :
    if os.environ.get ("RUN_MAIN") == "true" :
        thread.start_new_thread (main_func, args, kwargs)
        try:
            reloader_thread ()
        except KeyboardInterrupt:
            pass
    else:
        try:
            sys.exit (restart_with_reloader ())
        except KeyboardInterrupt:
            pass
# end def python_reloader

def jython_reloader (main_func, args, kwargs) :
    from _systemrestart import SystemRestart
    thread.start_new_thread (main_func, args)
    while True:
        if code_changed ():
            raise SystemRestart
        time.sleep (1)
# end def jython_reloader

def main (main_func, * args, ** kw):
    if sys.platform.startswith ('java'):
        reloader = jython_reloader
    else:
        reloader = python_reloader
    reloader (main_func, args, kw)
# end def main

if __name__ != "__main__" :
    from _GTW import GTW
    GTW._Export_Module ()
### __END__ GTW.autoreload
