#!/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify it under
# the terms of the (LGPL) GNU Lesser General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Library Lesser General Public License
# for more details at ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jurko Gospodnetić ( jurko.gospodnetic@pke.hr )

"""
Main installation and project management script for this project.

Attempts to use setuptools if available, and even attempts to install it
automatically if it is not, downloading it from PyPI if needed. However, its
main functionality will function just fine without setuptools as well. Having
setuptools available provides us with the following benefits:
  - simpler py2to3/distutils integration
  - setup.py 'egg_info' command constructing the project's metadata
  - setup.py 'develop' command deploying the project in 'development mode',
    thus making it available on sys.path, yet still editable directly in its
    source checkout - equivalent to running a pip based installation using
    'easy_install -e' or 'pip install -e'
  - setup.py 'test' command as a standard way to run the project's test suite
  - when running the installation directly from the source tree setup.py
    'install' command:
      - automatically installs the project's metadata so package management
        tools like pip recognize the installation correctly, e.g. this allows
        using 'pip uninstall' to undo the installation
      - package installed as a zipped egg by default

"""

import sys
import os
import os.path


# -----------------------------------------------------------------------------
# Import suds_devel module shared between setup & development scripts.
# -----------------------------------------------------------------------------

from setuptools import setup

# -----------------------------------------------------------------------------
# Support functions.
# -----------------------------------------------------------------------------





# Wrap long_description at 72 characters since the PKG-INFO package
# distribution metadata file stores this text with an 8 space indentation.
long_description = """
---------------------------------------
Lightweight SOAP client (Authentise's fork).
---------------------------------------

  Based on the Jurko suds project by Jurko Gospodnetić hosted at
https://bitbucket.org/jurko/suds

  Based on the original 'suds' project by Jeff Ortel (jortel at redhat
dot com) hosted at 'http://fedorahosted.org/suds'.

  'Suds' is a lightweight SOAP-based web service client for Python
licensed under LGPL (see the LICENSE.txt file included in the
distribution).

  This is hopefully just a temporary fork of the original suds Python
library project created because the original project development seems
to have stalled. Should be reintegrated back into the original project
if it ever gets revived again.

"""

setup(
    name="asuds",
    version="0.2",
    description="Lightweight SOAP client (Authentise's fork)",
    long_description=long_description,
    author="Jeff Ortel",
    author_email="jortel@redhat.com",
    keywords=["SOAP", "web", "service", "client"],
    url="http://bitbucket.org/Authentise/asuds",
    install_requires=[],
	zip_safe=True,
    packages=[
        "suds.sax",
        "suds.transport",
        "suds.xsd",
        "suds.mx",
        "suds.bindings",
        "suds",
        "suds.umx",
    ],

    maintainer="Eli Ribble",
    maintainer_email="eli@authentise.com",
    obsoletes="suds",
)
