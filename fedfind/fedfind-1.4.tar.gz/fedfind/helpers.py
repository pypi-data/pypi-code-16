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

"""Miscellaneous small functions that don't need to be class methods."""

import datetime
import logging
import os
# Upstream docs recommend using subprocess32 if possible, but make
# this optional as it's not available in EPEL.
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess
from six.moves.urllib.parse import urlparse
from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)

def date_check(value, fail_raise=True, out='obj'):
    """Checks whether a value is a date, and returns it if so. Valid
    dates are datetime.date instances or a string or int 'YYYYMMDD'.
    If out is set to 'obj', returns a datetime.date object. If out is
    set to 'both', returns a (string, object) tuple. If out is set to
    'str' (or anything else), returns a 'YYYYMMDD' string.

    On failure - empty or non-date-y input - will raise an exception
    if fail_raise is set, otherwise will return False.
    """
    if isinstance(value, datetime.date):
        dateobj = value
    else:
        try:
            dateobj = datetime.datetime.strptime(str(value), '%Y%m%d')
        except ValueError:
            if fail_raise:
                err = "{0} is not a valid date.".format(value)
                raise ValueError(err)
            else:
                return False

    if out == 'obj':
        return dateobj
    else:
        datestr = dateobj.strftime('%Y%m%d')
        if out == 'both':
            return (datestr, dateobj)
        else:
            return datestr

def url_exists(url):
    """Checks whether a URL exists, by trying to open it."""
    scheme = urlparse(url).scheme
    if 'http' in scheme:
        logger.debug("url_exists: checking %s as HTTP", url)
        try:
            urlopen(url)
            return True
        except (ValueError, URLError, HTTPError):
            return False
    elif 'rsync' in scheme:
        logger.debug("url_exists: checking %s as rsync", url)
        null = open(os.devnull)
        args = ('/usr/bin/rsync', url)
        # Doesn't use check_output as it's not in Python 2.6
        process = subprocess.Popen(args, stdout=null, stderr=null)
        process.communicate()
        retcode = process.poll()
        if retcode:
            return False
        return True

def comma_list(string):
    """Split a comma-separated list of values into a list (used by the
    CLI for passing query parameters etc).
    """
    return string.split(',')

def ci_match(val1, val2, exact, neg):
    """Case-insensitive match, handles either term being false-y. More
    or less expects strings; forces both values to str() to do the
    comparison so it tolerates ints (though it matches them like
    strings). Used by the query stuff.
    """
    logger.debug(
        "ci_match: comparing %s and %s, exact %s, neg %s",
        val1, val2, exact, neg)
    if not val1 and not val2:
        ret = True
    elif not val1 or not val2:
        ret = False
    elif exact:
        ret = str(val1).lower() == str(val2).lower()
    else:
        ret = str(val1).lower() in str(val2).lower()
    if neg:
        ret = not ret
    return ret

def cache_key_match(cacheopts, opts):
    """Used by the Koji search cache. Doing this inline is difficult
    due to flow control issues.
    """
    for (opt, value) in cacheopts.items():
        if opt in opts:
            # kojihub.py documents 'state' and 'arch' as the only
            # opts which take lists. We add 'method' (see find_nightly
            # _tasks() docstring).
            if opt in ('state', 'method', 'arch'):
                if not set(opts[opt]).issubset(set(value)):
                    return False
            else:
                if opts[opt] != value:
                    return False
    return True
