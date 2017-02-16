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

from __future__ import unicode_literals
from __future__ import print_function

import datetime
import json
import logging
import os
import re
import time
# Upstream docs recommend using subprocess32 if possible, but make
# this optional as it's not available in EPEL.
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess
from six.moves.urllib.parse import urlparse, urlencode
from six.moves.urllib.request import urlopen, Request
from six.moves.urllib.error import URLError, HTTPError
from productmd.images import (SUPPORTED_IMAGE_TYPES, SUPPORTED_IMAGE_FORMATS)
import productmd.composeinfo

import fedfind.const

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

def rsync_helper(args, output=False, retry=5):
    """Runs rsync with specified args. Returns a tuple of the retcode
    and a string. If output is False, the string will always be empty.
    If output is True, the string will contain the stdout output. If
    retry is >0 and rsync fails in a way that looks like some kind of
    connection error (for now just retcode '5' which is what we get
    when the server is overloaded), we'll retry that many times, 30
    seconds apart.
    """
    args = list(args)
    args.insert(0, '/usr/bin/rsync')
    null = open(os.devnull, 'w')
    if output:
        stdout = subprocess.PIPE
    else:
        stdout = null
    # Doesn't use check_output as it's not in Python 2.6
    process = subprocess.Popen(args, stdout=stdout, stderr=null)
    out = process.communicate()[0]
    retcode = process.poll()
    while retcode == 5 and retry:
        retry -= 1
        logger.debug("rsync_helper: server full! Retrying in 30 secs...")
        time.sleep(30)
        process = subprocess.Popen(args, stdout=stdout, stderr=null)
        out = process.communicate()[0]
        retcode = process.poll()
    if not out:
        out = u""
    # Handle the fact that this is bytes in py3 but str in py2
    else:
        out = out.decode()
    return (retcode, out)

def urlopen_retries(url, tries=5):
    """Simple attempt to open a URL and return the response, with
    retries.
    """
    tries = 5
    resp = None
    while not resp and tries:
        try:
            resp = urlopen(url)
        except (ValueError, URLError, HTTPError):
            logger.debug("HTTP error! Retrying...")
            tries -= 1
    if not resp:
        raise ValueError("urlopen_retries: Failed to open {0}!".format(url))
    return resp

def download_json(url):
    """Given a URL that should give us some JSON, download and return
    it.
    """
    resp = urlopen_retries(url)
    # We can't just use json.load on the response because of a bytes/
    # str type issue in Py3: https://stackoverflow.com/questions/6862770
    rawjson = resp.read().decode('utf8')
    return json.loads(rawjson)

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
        retcode = rsync_helper([url], False)[0]
        # 23 is the 'file not found' return code
        if retcode == 23:
            return False
        elif retcode == 5:
            raise IOError("url_exists: rsync server busy")
        elif retcode:
            raise IOError("Unexpected rsync error {0}!".format(retcode))
        return True
    else:
        raise ValueError("Invalid or unhandled URL!")

def get_size(url):
    """Get the size of URL (Content-Length header for HTTP). Currently
    only supports HTTP.
    """
    logger.debug("Checking size of %s", url)
    if not url.startswith('http'):
        raise ValueError("Can only check HTTP URLs for now.")
    headers = urlopen_retries(url).info()
    size = headers.getheader('Content-Length')
    if not size:
        raise ValueError("Size could not be found!")
    return int(size)

def comma_list(string):
    """Split a comma-separated list of values into a list (used by the
    CLI for passing query parameters etc). Also lower-cases the string
    because it's convenient to do that here...
    """
    return string.lower().split(',')

def get_current_release(branched=False):
    """Find out what the 'current' Fedora release is, according to
    the pkgdb API. If 'branched' is truth-y, will return the Branched
    release number if there is one.
    """
    logger.debug("get_current_release: finding current release")
    gotjson = download_json(
        'https://admin.fedoraproject.org/pkgdb/api/collections/')
    collections = gotjson['collections']
    if branched:
        rels = [coll['version'] for coll in collections if
                coll['status'] in ('Active', 'Under Development')]
    else:
        rels = [coll['version'] for coll in collections if
                coll['status'] == 'Active']
    rels = [int(rel) for rel in rels if rel.isdigit()]
    return max(rels)

def create_image_dict(path):
    """Synthesize a productmd-style image metadata dict by analyzing
    the image's path. Used for pre-Pungi 4 releases.
    """
    logger.debug("Synthesizing image metadata for %s", path)
    imgdict = {'path': path.strip('/')}
    path = path.lower()
    filename = path.split('/')[-1]

    # Find arch
    imgdict['arch'] = ""
    for arc in fedfind.const.ARCHES:
        if any(val in path for val in arc.values):
            imgdict['arch'] = arc.name

    # Find format
    imgdict['format'] = ""
    for form in SUPPORTED_IMAGE_FORMATS:
        if filename.endswith(form):
            imgdict['format'] = form

    # Find type
    imgdict['type'] = ""
    for typ in SUPPORTED_IMAGE_TYPES:
        # Some types are basically formats...
        if '-' in typ and typ.replace('-', '.') in filename:
            imgdict['type'] = typ
        # Others are more token-y.
        elif "-{0}-".format(typ) in filename:
            imgdict['type'] = typ
    # Sometimes we have to be a bit more relaxed.
    if not imgdict['type']:
        for typ in SUPPORTED_IMAGE_TYPES:
            if typ != "cd" and typ in filename:
                imgdict['type'] = typ
    # and this is just magic.
    if not imgdict['type'] and "disc" in filename:
        imgdict['type'] = "cd"
    # more magic! final names of Cloud Atomic installer images suck.
    if not imgdict['type'] and "cloud_atomic" in filename:
        # fedfind 1.x called these 'canned', but productmd has no
        # special type for them, considers them 'boot'.
        imgdict['type'] = "boot"

    return imgdict

def pdc_query(path, params=None):
    """Light 'API client', sorta, for PDC. Just handles sending a
    request to a given API path with the appropriate header to get
    a JSON response, parsing the response, and handling multi-page
    responses. params is a dict of query params.
    """
    results = []
    baseurl = '/'.join((fedfind.const.PDC_API, path.strip('/')))
    if not params:
        params = dict()
    params['page'] = '1'
    url = '?'.join((baseurl, urlencode(params)))
    headers = {'Content-type': 'application/json'}
    req = Request(url, headers=headers)
    nxt = True
    while nxt:
        resp = download_json(req)
        results.extend(resp['results'])
        params['page'] = str(int(params['page'])+1)
        url = '?'.join((baseurl, urlencode(params)))
        req = Request(url, headers=headers)
        nxt = resp['next']
    return results

def find_cid(string):
    """Find a Pungi 4 compose ID in a string."""
    cidpatt = re.compile(r'Fedora-.+-\d{8,8}(\.\w)?\.\d+')
    match = cidpatt.search(string)
    if match:
        return match.group(0)
    else:
        return ''

def parse_cid(cid):
    """Get release, date, type, and respin values from a Pungi 4
    compose id.
    """
    release = cid.split('-')[1].lower()
    (date, typ, respin) = productmd.composeinfo.get_date_type_respin(cid)
    return (release, date, typ, respin)

def cid_from_label(release, label):
    """Get the compose ID for a compose by label. Must also specify
    the release as labels are re-used per release. Uses PDC.
    """
    params = {'release': "fedora-{0}".format(release), 'compose_label': label}
    res = pdc_query('composes', params)
    if res:
        return res[0]['compose_id']
    return ''

def label_from_cid(cid):
    """Get the compose label for a compose by ID. Only completed
    production composes have discoverable labels; will return the
    empty string for other composes.
    """
    params = {'compose_id': cid}
    res = pdc_query('composes', params)
    if res:
        return res[0]['compose_label']
    return ''
