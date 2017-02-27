# -*- coding: utf-8 -*-
# Copyright (C) 2004-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    run_doctest
#
# Purpose
#    Run doctest on all modules specified on command line
#
# Revision Dates
#     8-Jan-2004 (CT) Creation
#    23-Feb-2004 (CT) `min_args = 1` added
#    20-Oct-2004 (CT) `_main` changed to use `sos.system` to test multiple
#                     modules in separate interpreter invocations (avoid
#                     interactions between the tests)
#    21-Oct-2004 (CT) `_main` changed to add path of module to be tested to
#                     `sys.path`
#    23-Oct-2004 (CT) `TFL.Package_Namespace._check_clashes` set to False
#     1-Jun-2005 (CT) `run_command` factored to take care of `PYTHONPATH`
#     2-Oct-2006 (CT) `replacer` added
#    11-Nov-2009 (CT) Support for directories added
#    19-Nov-2009 (CT) `has_doctest` added and used
#    17-Dec-2009 (CT) Pass `optionflags` to `doctest.testmod`:
#                       `doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF`
#    18-Dec-2009 (CT) `-nodiff` added to disable `doctest.REPORT_NDIFF`
#    29-Apr-2010 (MG) Support for running the doctest in optimized mode added
#    12-May-2010 (MG) Summary generation added
#    17-May-2010 (CT) `failures` added to `_main`
#    19-May-2010 (CT) Support for keywords->environment added
#                     (and ported to use TFL.CAO instead of TFL.Command_Line)
#    22-Jun-2010 (CT) Use `TFL.CAO.put_keywords` instead of
#                     `TFL.CAO.do_keywords` and home-grown code
#    11-Aug-2010 (CT) Summary generation totally revamped
#    11-Aug-2010 (CT) `_main` changed to avoid starting subprocesses for
#                     directory traversal (factored and changed `run_dir`)
#    11-Aug-2010 (CT) Option `-format` replaced by module-level variables
#                     `format_f` and `format_s`
#    17-Aug-2010 (CT) `__test__` added to `_doctest_pat`
#    14-Jun-2011 (MG) `timing` command line option added
#    10-Aug-2012 (MG) Add new command line option for `exclude`
#    17-Jan-2013 (CT) Add package-path to `sys.path`
#    29-Jan-2013 (CT) Improve DRY of _main
#     6-Aug-2013 (CT) Use `timeit.default_timer`, not `time.time`
#     6-Aug-2013 (CT) Print summary to `sys.stderr`
#     6-Aug-2013 (CT) Add number of test-cases to output
#     9-Dec-2013 (CT) Add call to `logging.disable`
#     9-Dec-2013 (CT) Use `utf-8`, not `latin-1`
#    31-Jan-2014 (CT) Use `sos.python_options` for spawned python interpreter
#    16-Jul-2015 (CT) Add `expect_except` to `module` before testing
#    14-Oct-2015 (CT) Add command line option `-RExclude`
#    16-Oct-2015 (CT) Add command line option `-Extra_Interpreters`
#    10-Oct-2016 (CT) Move to package namespace TFL
#    10-Oct-2016 (CT) Use `__file__`, not `TFL.Environment.script_name`
#    ««revision-date»»···
#--

from   __future__       import absolute_import
from   __future__       import division
from   __future__       import print_function
from   __future__       import unicode_literals

from   _TFL             import TFL
from   _TFL             import sos
from   _TFL.Filename    import Filename
from   _TFL.Regexp      import *
import _TFL.Record

import _TFL.Caller
import _TFL.CAO
import _TFL.Package_Namespace

from   timeit     import default_timer as _timer

import doctest
import logging
import sys
import subprocess
import fnmatch

TFL.Package_Namespace._check_clashes = False ### avoid spurious ImportErrors

_doctest_pat   = Regexp (r"^( *>>> |__test__ *=)", re.MULTILINE)

summary        = TFL.Record \
    ( cases    = 0
    , excluded = []
    , failed   = 0
    , failures = []
    , modules  = 0
    , total    = 0
    )

format_f = """%(module.__file__)s fails %(f)s of %(t)s doc-tests in %(cases)s test-cases%(et)s%(py_version)s"""
format_s = """%(module.__file__)s passes all of %(t)s doc-tests in %(cases)s test-cases%(et)s%(py_version)s"""
format_x = """%s  [py %s] raises exception `%r` during doc-tests%s"""
sum_pat  = Regexp \
    ( "(?P<module>.+?) (?:fails (?P<failed>\d+)|passes all) of "
      "(?P<total>\d+) doc-tests (?:in (?P<cases>\d+) test-cases)?"
    )
exc_pat  = Regexp \
    ("(?P<module>.*?) raises exception `(?P<exc>[^`]+)` during doc-tests")

def has_doctest (fn) :
    with open (fn, "rb") as f :
        code = f.read ()
    return _doctest_pat.search (code)
# end def has_doctest

def run_command (cmd) :
    subp = subprocess.Popen (cmd, shell = True, env = dict (sos.environ))
    subp.wait ()
# end def run_command

def _subp_step (subp) :
    try :
        out, err = subp.communicate ()
    except ValueError :
        pass
    else :
        err = err.decode ("utf-8")
        out = out.decode ("utf-8")
        sys.stdout.write (out)
        sys.stderr.write (err)
        if err :
            for l in err.split ("\n") :
                if sum_pat.match (l) :
                    summary.total += int (sum_pat.total)
                    summary.cases += int (sum_pat.cases or 1)
                    f = int (sum_pat.failed or 0)
                    if f :
                        summary.failed += f
                        summary.failures.append ((sum_pat.module, f))
                elif exc_pat.match (l) :
                    summary.failed += 1
                    summary.total  += 1
                    summary.failures.append \
                        ((exc_pat.module, "Exception %s" % (exc_pat.exc, )))
# end def _subp_step

def run_command_with_summary (cmd) :
    subp = subprocess.Popen \
        ( cmd
        , shell   = True
        , env     = dict (sos.environ)
        , stderr  = subprocess.PIPE
        , stdout  = subprocess.PIPE
        )
    while subp.poll () is None :
        _subp_step (subp)
    _subp_step (subp)
# end def run_command_with_summary

def _main (cmd) :
    cmd_path   = list (cmd.path or [])
    replacer   = Re_Replacer (r"\.py[co]", ".py")
    a          = cmd.argv [0]
    et         = ""
    one_arg_p  = len (cmd.argv) == 1 and not sos.path.isdir (a)
    if one_arg_p and not cmd.Extra_Interpreters :
        f              = Filename (a)
        m              = f.base
        py_version     = " [py %s]" % \
            ".".join (str (v) for v in sys.version_info [:3])
        sys.path [0:0] = cmd_path
        mod_path       = f.directory if f.directory else "./"
        if sos.path.exists \
               (Filename ("__init__.py", default_dir = mod_path).name) :
            sys.path [0:0] = [sos.path.join (mod_path, "..")]
        sys.path [0:0] = [mod_path]
        flags = doctest.NORMALIZE_WHITESPACE
        if not cmd.nodiff :
            flags |= doctest.REPORT_NDIFF
        try :
            logging.disable (logging.WARNING)
            start  = _timer ()
            module = __import__ (m)
            module.expect_except = TFL.CAO.expect_except
            cases  = len (getattr (module, "__test__", ())) or 1
            f, t   = doctest.testmod \
                ( module
                , verbose     = cmd.verbose
                , optionflags = flags
                )
            exec_time = _timer () - start
        except KeyboardInterrupt :
            raise
        except Exception as exc :
            exec_time = _timer () - start
            if cmd.timing :
                et = " in %7.5fs" % (exec_time, )
            msg = format_x % (replacer (a), py_version, exc, et)
            print (msg, file = sys.stderr)
            raise
        else :
            format = format_f if f else format_s
            if cmd.timing :
                et = " in %7.5fs" % (exec_time, )
            print (replacer (format % TFL.Caller.Scope ()), file = sys.stderr)
    else :
        py_executables = [sys.executable] + list (cmd.Extra_Interpreters)
        py_version     = ""
        head_pieces    = sos.python_options () + \
            [ __file__
            , "-path %r" % (",".join (cmd_path), ) if cmd_path else ""
            ]
        for opt in ("nodiff", "timing", "verbose") :
            if getattr (cmd, opt) :
                head_pieces.append ("-" + opt)
        head = " ".join (hp for hp in head_pieces if hp)
        if cmd.summary :
            run_cmd = run_command_with_summary
        else :
            run_cmd = run_command
        if cmd.RExclude :
            x_pat   = Regexp (cmd.RExclude)
            exclude = x_pat.search
        elif cmd.exclude :
            exclude = lambda a : fnmatch.fnmatch (a, cmd.exclude)
        else :
            exclude = lambda a : False
        def run_mod (a) :
            if exclude (a) :
                summary.excluded.append (a)
                print ("%s excluded" % (a, ))
            else :
                summary.modules += 1
                for pyx in py_executables :
                    run_cmd ("%s %s %s" % (pyx, head, a))
        def run_mods (d) :
            for f in sorted (sos.listdir_exts (d, ".py")) :
                if has_doctest (f) :
                    run_mod (f)
        if cmd.transitive :
            from _TFL.subdirs import subdirs
            def run_dir (d) :
                run_mods (d)
                for s in subdirs (d) :
                    run_dir (s)
        else :
            run_dir = run_mods
        start = _timer ()
        for a in cmd.argv :
            if sos.path.isdir (a) :
                run_dir (a)
            else :
                if has_doctest (a) :
                    run_mod (a)
        if cmd.summary :
            format = format_f if summary.failed else format_s
            if cmd.timing :
                et = " in %7.5fs" % (_timer () - start, )
            print ("=" * 79, file = sys.stderr)
            print \
                ( format % TFL.Caller.Scope
                    ( f      = summary.failed
                    , module = TFL.Record (__file__ = " ".join (cmd.argv))
                    , t      = summary.total
                    , cases  = summary.cases
                    , et     = et
                    )
                , "[%s/%s modules fail]" %
                    (len (summary.failures), summary.modules)
                , file = sys.stderr
                )
            print \
                ( "    %s"
                % ("\n    ".join ("%-68s : %s" % f for f in summary.failures))
                , file = sys.stderr
                )
            if summary.excluded :
                print \
                    ("    %s excluded" % (", ".join (summary.excluded), )
                    , file = sys.stderr
                    )
# end def _main

Command = TFL.CAO.Cmd \
    ( handler      = _main
    , args         = ("module:P?Module(s) to test", )
    , opts         =
        ( "exclude:S?Glob pattern to exclude certain tests"
        , "Extra_Interpreters:P:?Extra python interpreters to run tests through"
        , "nodiff:B?Don't specify doctest.REPORT_NDIFF flag"
        , "path:P:?Path to add to sys.path"
        , "RExclude:S?Regular expression to exclude certain tests"
        , "summary:B?Summary of failed tests"
        , "timing:B?Add timing information"
        , "transitive:B"
            "?Include all subdirectories of directories specified "
              "as arguments"
        , "verbose:B?Turn verbosity on"
        )
    , min_args     = 1
    , put_keywords = True
    )

if __name__ != "__main__" :
    TFL._Export_Module ()
else :
    Command ()
### __END__ run_doctest
