# -*- coding: utf-8 -*-
# Copyright (C) 2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package TFL_STP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL_STP.__init__
#
# Purpose
#    Package with helper functions for setup.py for TFL-based packages
#
# Revision Dates
#    23-Feb-2017 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function

### `unicode_literals` break `distutils`
### https://bugs.python.org/issue13943 (Created on 2012-02-04 20:41)
### from   __future__  import unicode_literals

from   .           import fs_find

from   codecs      import open
from   setuptools  import Command, find_packages

import ast
import itertools
import os
import re
import subprocess
import sys

if sys.version_info < (3,) :
    def as_str (x) :
        try :
            encode = x.encode
        except AttributeError :
            return str (x)
        else :
            return encode ("utf-8", "replace")
else :
    def as_str (x) :
        try :
            decode = x.decode
        except AttributeError :
            return str (x)
        else :
            return decode ("utf-8", "replace")

version_py_fmt  = """\
__date__    = "%(date)s"
__version__ = "%(tagged_version)s"
"""

version_re      = re.compile (r"__version__\s+=\s+(.*)")

class Test_Command (Command) :

    user_options = []

    _test_args_h = []
    _test_args   = ["-summary", "-transitive", "./"]
    _test_args_t = []

    @classmethod
    def NEW (cls, head_args = [], args = [], tail_args = [], ** kwds) :
        if head_args :
            kwds.update (_test_args_h = head_args)
        if args :
            kwds.update (_test_args   = args)
        if tail_args :
            kwds.update (_test_args_t = tail_args)
        name = str ("%s__%s" % (cls.__name__, id (kwds)))
        return type (cls) (name, (cls, ), kwds)
    # end def NEW

    def initialize_options (self) : pass
    def finalize_options   (self) : pass

    def run (self) :
        from _TFL import run_doctest
        return run_doctest.Command \
            (self._test_args_h + self._test_args + self._test_args_t)

# end class Test_Command

def change_to_dir (file_name) :
    """Change to source directory of file named `file_name`"""
    src_dir = os.path.dirname (file_name)
    if src_dir :
        os.chdir (src_dir)
    return src_dir
# end def change_to_dir

def git_date_version (abort_on_error = True) :
    """Get date and version from `git` if inside a git sandbox."""
    try :
        date = run_command \
            (["git", "log", "--format=format:%cI", "-1"])
    except subprocess.CalledProcessError as exc :
        ### `git` isn't available of current directory isn't a sandbox
        return
    try :
        tagged_version = run_command \
            ( [ "git", "describe"
              , "--tags", "--first-parent", "--dirty=-modified"
              , "--match", "[0-9]*.[0-9]*"
              ]
            )
    except subprocess.CalledProcessError as exc :
        if abort_on_error :
            print ("Please use `git tag` to define your package's version.")
            raise SystemExit (128)
        else :
            raise
    tagged_version = tagged_version.replace ("-", "+", 1).replace ("-", ".")
    return date, tagged_version
# end def git_date_version

def long_description () :
    """Get long description from file `README.rst`"""
    return open ("README.rst", encoding = "utf-8").read ().strip ()
# end def long_description

def packages_plus_data_files (p_name, * extras) :
    """Find packages, data directories, and data files to include"""
    Q          = fs_find.Filter
    packages   = [p_name] \
               + list (".".join ((p_name, p)) for p in find_packages ())
    data_dirs  = fs_find.directories \
        ( ".", filter = Q (include = Q.IN ("-I18N", "locale")))
    data_files = list \
        ( itertools.chain
            ( ["LICENSE", "README.rst", "setup.py", "setup.cfg", "stp.cfg"]
            , extras
            , fs_find.file_iter
                (".", filter = Q (include = Q.equal ("babel.cfg")))
            , fs_find.file_iter (* data_dirs)
            )
        )
    return packages, data_files
# end def packages_plus_data_files

def package_version () :
    """Get package version from `get` or `VERSION.py`."""
    result = update_version_py ()
    if result is None :
        try :
            with open ("VERSION.py", encoding = "utf-8") as f :
                version_py = f.read ()
        except IOError as exc :
            result = None
        else :

            result = str \
                (ast.literal_eval (version_re.search (version_py).group (1)))
    if not result :
        print ("Neither `git` nor `VERSION.py` supply this package's version.")
        raise SystemExit (128)
    return result
# end def package_version

def run_command (cmd, ** kwds) :
    result = subprocess.check_output (cmd, stderr = subprocess.STDOUT, ** kwds)
    return as_str (result).strip ()
# end def run_command

def update_version_py () :
    """Update `VERSION.py` in current directory with git version info."""
    d_v = git_date_version ()
    if d_v :
        date, tagged_version = d_v
        version_py = version_py_fmt % dict \
            (date = date, tagged_version = tagged_version)
        with open ("VERSION.py", "w", encoding = "utf-8") as f :
            f.write (version_py)
        return tagged_version
# end def update_version_py

### __END__ TFL_STP.__init__
