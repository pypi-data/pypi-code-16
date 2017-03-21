# -*- coding: utf-8 -*-
# Copyright (C) Patrick Brady, Brian Moe, Branson Stephens (2015)
#
# This file is part of lvalert
#
# lvalert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lvalert.  If not, see <http://www.gnu.org/licenses/>.
# 

import os

from setuptools import setup, find_packages

version = "1.4.3"

setup(
  name = "ligo-lvalert",
  version = version,
  maintainer = "Tanner Prestegard, Alexander Pace, Branson Stephens",
  maintainer_email = "tanner.prestegard@ligo.org, alexander.pace@ligo.org, branson.stephens@ligo.org",
  description = "LIGO-Virgo Alert Network",
  long_description = "The LIGO-Virgo Alert Network (LVAlert) is a prototype notification service built XMPP to provide a basic notification tool which allows multiple producers and consumers of notifications.",

  url = "https://wiki.ligo.org/DASWG/LVAlert",
  license = 'GPL',
  namespace_packages = ['ligo'],
#  provides = ['ligo.lvalert'],
  packages = find_packages(),

  requires = ['pyxmpp', 'libxml2', 'M2Crypto', 'dnspython'],

  scripts = [
    os.path.join('bin','lvalert_admin'),
    os.path.join('bin','lvalert_send'),
    os.path.join('bin','lvalert_listen'),
  ],

)

# Dependencies.

# Python name     RHEL Name       Debian name
# (easy_install)  (yum)           (apt-get)
# 
# pyxmpp          pyxmpp *        python-pyxmpp
# libxml2 **      libxml2-python  python-libxml2
# M2Crypto        m2crypto        python-m2crypto
# dnspython       python-dns      python-dnspython
#
#   * lscsoft package
# 
#  ** Not in normal easy_install/pip place.  Also requires swig if installing with pip.
#        sudo apt-get install swig
#        pip install ftp://xmlsoft.org/libxml2/python/libxml2-python-2.6.9.tar.gz

