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

import copy
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
    size = headers.get('Content-Length')
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
    the image's path. Used for pre-Pungi 4 releases, and Pungi 4
    releases that were split and had metadata stripped when synced to
    mirrors.
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
    # we invent a types for the 'multiple' images that contain
    # multiple live or installer images together with a boot menu.
    # these will have 'Multi' subvariant
    types = SUPPORTED_IMAGE_TYPES + ['multi-desktop', 'multi-install']
    for typ in types:
        # Some types are basically formats...
        if '-' in typ and typ.replace('-', '.') in filename:
            imgdict['type'] = typ
        # Others are more token-y.
        elif "-{0}-".format(typ) in filename:
            imgdict['type'] = typ
    # Sometimes we have to be a bit more relaxed.
    if not imgdict['type']:
        for typ in types:
            if typ != "cd" and typ in filename:
                imgdict['type'] = typ
    # and this is just magic.
    if not imgdict['type'] and "disc" in filename:
        imgdict['type'] = "cd"
    # Various special handlings for awkward ostree installer images
    # Since 2016-10-10 with up-to-date Pungi the filenames should have
    # -ostree- in them...
    if '-ostree-' in filename:
        imgdict['type'] = "dvd-ostree"
    # ...but as of 2016-10-08 F24 two-week Atomic composes, the
    # filename is e.g.: Fedora-Atomic-dvd-x86_64-24-20161008.0.iso
    if '-atomic-dvd-' in filename:
        imgdict['type'] = "dvd-ostree"
    # F23 release case: Fedora-Cloud_Atomic-x86_64-23.iso
    if imgdict['type'] in ("", "dvd") and "cloud_atomic" in filename:
        imgdict['type'] = "dvd-ostree"
    # awkward case from F25 Beta, where we got a Workstation atomic
    # installer image with a bad filename:
    # Fedora-Workstation-dvd-x86_64-25_Beta-1.1.iso
    # probably too broad to keep forever, drop when 25 Beta is gone
    if '-workstation-dvd-' in filename:
        imgdict['type'] = "dvd-ostree"

    # Find subvariant
    imgdict['subvariant'] = ''
    # these are a couple of nasty special cases taken
    # from fedfind 1.x
    if re.match(r'.*Fedora-(x86_64|i386)-\d{2,2}-\d{8,8}'
                r'(\.\d|)-sda\.(qcow2|raw.xz)',
                imgdict['path']):
        # F19/20-era cloud image, before Cloud flavor.
        imgdict['subvariant'] = 'Cloud'

    if re.match(r'.*(Fedora-|F)\d{1,2}-(x86_64|i686|Live)'
                r'-(x86_64|i686|Live)\.iso', imgdict['path']):
        # < F14 Desktop lives. Ew.
        imgdict['subvariant'] = 'Desktop'

    for load in fedfind.const.SUBVARIANTS:
        if any(val in imgdict['path'].lower()
               for val in load.values):
            imgdict['subvariant'] = load.name
    # Try to identify 'generic' media (call them
    # 'Everything' as that's what productmd does)
    if not imgdict['subvariant'] and (imgdict['type'] in
                                      ('dvd', 'boot', 'netinst', 'cd')):
        imgdict['subvariant'] = 'Everything'

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
        params = []
    # turn param dict into tuple list (we need to handle both dicts
    # and tuple lists, and you can't always turn a tuple list into a
    # dict because parameter names can be repeated)
    try:
        params = list(params.items())
    except AttributeError:
        pass
    pgcnt = 1
    params.append(('page', str(pgcnt)))
    url = '?'.join((baseurl, urlencode(params)))
    headers = {'Content-type': 'application/json'}
    req = Request(url, headers=headers)
    nxt = True
    while nxt:
        resp = download_json(req)
        try:
            # paged query
            results.extend(resp['results'])
            params.remove(('page', str(pgcnt)))
            pgcnt += 1
            params.append(('page', str(pgcnt)))
            url = '?'.join((baseurl, urlencode(params)))
            req = Request(url, headers=headers)
            nxt = resp['next']
        except KeyError:
            # non-paged query. just return
            return resp
    return results

def find_cid(string):
    """Find a Pungi 4 compose ID in a string."""
    cidpatt = re.compile(r'Fedora-.+-\d{8,8}(\.\w)?\.\d+')
    match = cidpatt.search(string)
    if match:
        return match.group(0)
    else:
        return ''

def parse_cid(origcid):
    """Get release, date, type, and respin values from a Pungi 4
    compose id.
    """
    # Normalize and check cid
    cid = find_cid(origcid)
    if not cid:
        raise ValueError("{0} does not appear to be a valid Pungi 4 Fedora "
                         "compose ID!".format(origcid))
    release = cid.split('-')[-2].lower()
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
    typ = parse_cid(cid)[2]
    if typ != 'production':
        return ''
    params = {'compose_id': cid}
    res = pdc_query('composes', params)
    if res:
        return res[0]['compose_label']
    return ''

def get_weight(imgdict, arch=True):
    """Given a productmd image dict, return a number that tries to
    represent how 'important' that image is. This is intended for use
    in producing things like download tables, so you can order the
    images sensibly. Used for e.g. wikitcms download tables. Consider
    arch if arch is truth-y, otherwise don't.
    """
    archscores = (
        (('x86_64', 'i386'), 2000),
    )
    loadscores = (
        (('everything',), 300),
        (('workstation',), 220),
        (('server',), 210),
        (('cloud', 'desktop', 'cloud_base', 'docker_base', 'atomic'), 200),
        (('kde',), 190),
        (('minimal',), 90),
        (('xfce',), 80),
        (('soas',), 73),
        (('mate',), 72),
        (('cinnamon',), 71),
        (('lxde',), 70),
        (('source',), -10),
    )
    imgscore = 0
    if arch:
        for (values, score) in archscores:
            if imgdict['arch'] in values:
                imgscore += score
    for (values, score) in loadscores:
        if imgdict['subvariant'].lower() in values:
            imgscore += score
    return imgscore

def correct_image(imgdict):
    """This function is intended to make 'corrections' to the image
    dict to handle cases where the metadata produced by pungi are
    problematic. The passed dict is copied and the modified dict
    returned.
    """
    newdict = copy.deepcopy(imgdict)
    # ostree installer images get type 'boot', but this is unviable
    # because network install images also get type 'boot' and thus
    # we cannot distinguish between an ostree installer image and a
    # network install image for the same subvariant, and since
    # 2016-10, Fedora has both a Workstation network install image
    # and a Workstation ostree installer image. This is filed as
    # https://pagure.io/pungi/issue/417 . Until it gets fixed, we'll
    # work around it here, by substituting the proposed 'dvd-ostree'
    # type value.
    if imgdict['type'] == 'boot':
        filename = imgdict['path'].split('/')[-1]
        if '-dvd-' in filename or '-ostree-' in filename:
            newdict['type'] = 'dvd-ostree'
    return newdict

def identify_image(imgdict, out='tuple', undersub=False, lower=False):
    """Produce an 'image identifier' from the image dict. We use the
    combination of subvariant, type, and format to 'identify' a given
    image all over the place; by having them all use this function we
    can make sure they're all consistent, handle special cases and
    ease changing the identifier in future if necessary. If 'out' is
    'string', you get a single string joined with dashes. If 'out' is
    'tuple', you get a tuple. If 'undersub' is true, dashes in the
    metadata values will be replaced by underscores (this is so the
    string form can be reliably split into the component parts). If
    lower is True, values will be forced to all lower case.
    """
    # 'correct' the imgdict first
    imgdict = correct_image(imgdict)

    # get the values
    subv = imgdict['subvariant']
    typ = imgdict['type']
    form = imgdict['format']

    if undersub:
        # sub - to _
        subv = subv.replace('-', '_')
        typ = typ.replace('-', '_')
        form = form.replace('-', '_')

    if lower:
        # lowercase
        subv = subv.lower()
        typ = typ.lower()
        form = form.lower()

    # construct the tuple
    ret = (subv, typ, form)

    if out == 'string':
        # produce the string
        ret = '-'.join(ret)

    return ret
