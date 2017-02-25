#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Mag. Christian Tanzer. All rights reserved
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
#    _GTW.setup
#
# Purpose
#    Setup file for package namespace GTW
#
# Revision Dates
#    12-Oct-2016 (CT) Creation
#    13-Oct-2016 (CT) Use `find_packages`, `_TFL.fs_find`, not home-grown code
#    22-Feb-2017 (CT) Use `TFL_STP`, not home-grown code
#    25-Feb-2017 (CT) Pass `data_dirs` to `packages_plus_data_files`
#    ««revision-date»»···
#--

from   __future__               import print_function

from   setuptools               import setup

import TFL_STP as STP

STP.change_to_dir (__file__)

license = "BSD License"
name    = "GTW"
p_name  = "_GTW"

version              = STP.package_version ()
long_description     = STP.long_description ()
packages, data_files = STP.packages_plus_data_files \
    (p_name, data_dirs = ["media"])
Test_Command         = STP.Test_Command.NEW \
    (head_args = ["GTW_test_backends=sq"])

if __name__ == "__main__" :
    setup \
    ( name                 = name
    , version              = version
    , description          =
        "A werkzeug-based framework for RESTful web applications"
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
        , "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
        , "Topic :: Software Development :: Libraries :: Python Modules"
        , "Topic :: Text Processing :: Markup :: HTML"
        ]
    , setup_requires       = ["TFL_STP"]
    , install_requires     =
        [ "CAL", "CHJ", "JNJ", "MOM-Tapyr", "ReST-Tapyr", "TFL"
        , "python-dateutil", "pillow", "werkzeug"
        ]
    , extras_require       = dict
        ( client_certificate   = ["M2Crypto", "pyspkac"]
        , convert_rtr_at_data  = ["xlrd"]
        , deploy               = ["plumbum"]
        , fastcgi              = ["flup"]
        , markdown             = ["markdown"]
        , omp_net              = ["rsclib"]
        , rest_client          = ["requests"]
        , test                 =
            ["jinja2", "lxml", "pyquery", "requests", "sqlalchemy"]
        )
    , cmdclass             = dict (test = Test_Command)
    , zip_safe             = False ### no eggs, please
    )

### __END__ _GTW.setup
