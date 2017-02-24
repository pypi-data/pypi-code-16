#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2017 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria.
# Web: http://www.c-tanzer.at/en/ Email: tanzer@swing.co.at
# All rights reserved
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    _TFL.setup
#
# Purpose
#    Setup file for package namespace TFL
#
# Revision Dates
#    25-Oct-2007 (RS) Creation
#     7-Nov-2007 (CT) Add info, use `if` instead of `assert`
#    26-May-2011 (CT) Change file encoding to `iso-8859-15`
#    18-Nov-2013 (CT) Change file encoding to `utf-8`
#     3-Oct-2014 (CT) Replace `svn` by `git`
#     3-Oct-2014 (CT) Filter out `__pycache__` directories
#    10-Oct-2016 (CT) Get `__version__` from `__init__`
#    10-Oct-2016 (CT) Get `long_description` from `README`
#    10-Oct-2016 (CT) Use `setuptools`, not `distutils.core`
#    13-Oct-2016 (CT) Use `find_packages`, `_TFL.fs_find`, not home-grown code
#    22-Feb-2017 (CT) Factor `TFL_STP`
#    ««revision-date»»···
#--

from   __future__               import print_function

from   setuptools               import setup

import TFL_STP as STP

STP.change_to_dir (__file__)

license = "BSD License"
name    = "TFL"
p_name  = "_TFL"

version              = STP.package_version ()
long_description     = STP.long_description ()
packages, data_files = STP.packages_plus_data_files (p_name)
Test_Command         = STP.Test_Command

if __name__ == "__main__" :
    setup \
    ( name                 = name
    , version              = version
    , description          =
        "Library with lots of useful stuff (says Ralf Schlatterbeck)"
    , long_description     = long_description
    , license              = license
    , author               = "Christian Tanzer"
    , author_email         = "tanzer@swing.co.at"
    , url                  = "https://github.com/Tapyr/tapyr"
    , packages             = packages
    , package_dir          = { p_name : "." }
    , package_data         = { p_name : data_files }
    , platforms            = "Any"
    , classifiers          = \
        [ "Development Status :: 5 - Production/Stable"
        , "License :: OSI Approved :: " + license
        , "Operating System :: OS Independent"
        , "Programming Language :: Python"
        , "Programming Language :: Python :: 2"
        , "Programming Language :: Python :: 2.7"
        , "Programming Language :: Python :: 3"
        , "Programming Language :: Python :: 3.5"
        , "Intended Audience :: Developers"
        , "Topic :: Software Development :: Libraries :: Python Modules"
        ]
    , setup_requires       = ["TFL_STP"]
    , install_requires     = ["TFL_STP"]
    , extras_require       = dict
        ( bcrypt               = ["bcrypt"]
        , doc                  = ["plumbum", "sphinx"]
        , html_cleaner         = ["bs4"]
        , human_friendly_hsl   = ["husl"]
        , I18N                 = ["babel"]
        , timezone_support     = ["python-dateutil"]
        )
    , cmdclass             = dict (test = Test_Command)
    , zip_safe             = False ### no eggs, please
    )

### __END__ _TFL.setup
