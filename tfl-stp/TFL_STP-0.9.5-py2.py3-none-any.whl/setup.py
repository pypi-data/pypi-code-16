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
#    TFL_STP.setup
#
# Purpose
#    Setup file for package TFL_STP
#
# Revision Dates
#    23-Feb-2017 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import print_function

### `unicode_literals` break `distutils`
### https://bugs.python.org/issue13943 (Created on 2012-02-04 20:41)
### from   __future__  import unicode_literals

from   codecs      import open
from   setuptools  import setup
import os

src_dir = os.path.dirname (__file__)
if src_dir :
    os.chdir (src_dir)

license = "BSD License"
name    = "TFL_STP"
p_name  = "TFL_STP"

long_description = open ("README.rst", encoding = "utf-8").read ().strip ()
packages         = [ p_name ]
data_files       = ["LICENSE", "README.rst", "setup.py", "setup.cfg"]

if __name__ == "__main__" :
    setup \
    ( name                 = name
    , version              = "0.9.5"
    , description          = "Setup helper functions for TFL-based packages"
    , long_description     = long_description
    , license              = license
    , author               = "Christian Tanzer"
    , author_email         = "tanzer@swing.co.at"
    , url                  = "https://github.com/Tapyr/tapyr"
    , packages             = packages
    , package_dir          = { p_name : "." }
    , package_data         = { p_name : data_files }
    , platforms            = "Any"
    , include_package_data = True
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
    , setup_requires       = []
    , install_requires     = []
    , zip_safe             = False ### no eggs, please
    )

### __END__ TFL_STP.setup
