#!/bin/python2

# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>
#
# This file contains miscellaneous small helper functions.

import datetime
import os
import subprocess32
import urllib2

from urlparse import urlparse

def datecheck(string):
    """Checks whether a string is a date in YYYYMMDD format, or...not."""
    try:
        date = datetime.datetime.strptime(string, '%Y%m%d')
        return date
    except:
        return False

def url_exists(url):
    """Checks whether a URL exists, by trying to open it."""
    scheme = urlparse(url).scheme
    if 'http' in scheme:
        try:
            urllib2.urlopen(url)
            return True
        except:
            return False
    elif 'rsync' in scheme:
        null = open(os.devnull)
        try:
            args = ('/usr/bin/rsync', url)
            out = subprocess32.check_call(args, stdout=null,
                                          stderr=null)
            return True
        except:
            return False
