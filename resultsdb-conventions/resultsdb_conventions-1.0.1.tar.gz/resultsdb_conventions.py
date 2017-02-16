# Copyright (C) Adam Williamson
#
# resultsdb_conventions is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:   Adam Williamson <awilliam@redhat.com>

"""OO representation of conventions for reporting various types of
result to ResultsDB.
"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
import uuid

from cached_property import cached_property
import fedfind.helpers
import fedfind.release

# pylint:disable=invalid-name
logger = logging.getLogger(__name__)

# UTILITY FUNCTIONS

def uuid_namespace(name, namespace=None):
    """Create a UUID using the provided name and namespace (or default
    DNS namespace), handling string type and encoding ickiness on both
    Py2 and Py3.
    """
    # so the deal here is the passed name may be a string or a unicode
    # in Python 2 (for Python 3 we assume it's a string), and what we
    # need back is a string - not a bytestring on Python 3, or a
    # unicode on Python 2, as uuid doesn't accept either - with non-
    # ASCII characters stripped (as uuid doesn't accept those either).
    # This magic formula seems to work and produce the same UUID on
    # both.
    if not namespace:
        namespace = uuid.NAMESPACE_DNS
    return uuid.uuid5(namespace, str(name.encode('ascii', 'ignore').decode()))

# EXCEPTIONS

class ValidationError(Exception):
    """Validation error class."""
    def __init__(self, prop, value, desc):
        self.property = prop
        self.value = value
        self.desc = desc
        super(ValidationError, self).__init__(str(self))

    def __str__(self):
        return "Value {0} for property {1} is {2}".format(self.value, self.property, self.desc)

# RESULT CLASSES


class Result(object):
    """Base class for a single result. The signature follows the API
    create_result class as closely as possible. outcome is the actual
    result of the test ('PASSED', 'FAILED' etc.) tc_name is the test
    case name. groups may be an iterable of UUID strings or ResultsDB
    group instances; if set, the Result will be added to all the
    groups. note is the freeform text note. ref_url is the URL for
    this specific result, tc_url is the general URL for the testcase.
    source is the source of the result - something like 'openqa' or
    'autocloud'.
    """
    def __init__(self, outcome, tc_name, groups=None, note='', ref_url='', tc_url='', source=''):
        self.outcome = outcome
        self.tc_name = tc_name
        self.note = note
        self.ref_url = ref_url
        self.tc_url = tc_url
        self.source = source
        self.extradata = {}
        self.groups = []
        if groups:
            self.groups.extend(groups)

    @property
    def testcase_object(self):
        """The testcase object for this result."""
        return {
            "name": self.tc_name,
            "ref_url": self.tc_url,
        }

    def validate(self):
        """Check if the contents of the result are valid. We do not
        actually do any validation at this level - we cannot logically
        declare any conventions beyond what ResultsDB will accept, and
        the API will refuse any flat out invalid result.
        """
        pass

    def default_extradata(self):
        """If we have a source, add it to extradata."""
        if self.source:
            extradata = {'source': self.source}
            # doing things this way around means we don't override
            # existing values, only add new ones
            extradata.update(self.extradata)
            self.extradata = extradata

    def add_group(self, namespace, group_name, **extraparams):
        """Create a group dict and add it to the instance group list,
        using the normal convention for creating ResultsDB groups.
        The description of the group will be 'namespace.group' and
        the UUIDs are created from those values in a kinda agreed-upon
        way. Any extra params for the group can be passed in."""
        uuidns = uuid_namespace(namespace)
        groupdict = {
            'uuid': str(uuid_namespace(group_name, uuidns)),
            'description': '.'.join((namespace, group_name))
        }
        groupdict.update(**extraparams)
        self.groups.append(groupdict)

    def default_groups(self):
        """If we have a source, add a generic source group."""
        # NOTE: we could add a generic test case group, like there is
        # for Taskotron results, but I don't think it's any use
        if self.source:
            self.add_group('source', self.source)

    def report(self, rdbinstance, default_extradata=True, default_groups=True):
        """Report this result to ResultsDB. rdbinstance is an instance
        of ResultsDBapi. May pass through an exception raised by the
        API instance `create_result` method.
        """
        self.validate()
        if default_extradata:
            self.default_extradata()
        if default_groups:
            self.default_groups()
        logger.debug("Result: %s", self.outcome)
        logger.debug("Testcase object: %s", self.testcase_object)
        logger.debug("Groups: %s", self.groups)
        logger.debug("Job link (ref_url): %s", self.ref_url)
        logger.debug("Extradata: %s", self.extradata)
        if rdbinstance:
            return rdbinstance.create_result(outcome=self.outcome, testcase=self.testcase_object, groups=self.groups,
                                             note=self.note, ref_url=self.ref_url, **self.extradata)


class ComposeResult(Result):
    """Result from testing of a distribution compose. cid is the
    compose id. May raise ValueError via parse_cid. See Result for
    required args.
    """
    def __init__(self, cid, *args, **kwargs):
        super(ComposeResult, self).__init__(*args, **kwargs)
        self.cid = cid
        # item is always the compose ID (unless subclass overrides)
        self.extradata.update({
            'item': cid,
            'type': 'compose',
        })

    def default_extradata(self):
        """Get productmd compose info via fedfind and update extradata."""
        super(ComposeResult, self).default_extradata()
        (dist, release, date, imgtype, respin) = fedfind.helpers.parse_cid(self.cid, dist=True)
        extradata = {
            'productmd.compose.name': dist,
            'productmd.compose.version': release,
            'productmd.compose.date': date,
            'productmd.compose.type': imgtype,
            'productmd.compose.respin': respin,
            'productmd.compose.id': self.cid,
        }
        extradata.update(self.extradata)
        self.extradata = extradata

    def default_groups(self):
        """Add to generic result group for this compose."""
        super(ComposeResult, self).default_groups()
        extraparams = {}
        # get compose location if we can
        try:
            rel = fedfind.release.get_release(cid=self.cid)
            extraparams['ref_url'] = rel.location
        except ValueError:
            logger.warning("fedfind found no release for compose ID %s, compose group will have no URL", self.cid)
        self.add_group('compose', self.cid, **extraparams)
        if self.source:
            # We cannot easily do a URL here, unless we start having
            # a store of 'known' sources and how URLs are built for
            # them, or using callbacks, or something. I think we might
            # just ask downstreams to get the group from the group
            # list and add the URL to it?
            self.add_group(self.source, self.cid)


class FedoraImageResult(ComposeResult):
    """Result from testing a specific image from a compose. filename
    is the image filename. May raise ValueError via get_release
    or directly. See Result for required args.
    """
    def __init__(self, cid, filename, *args, **kwargs):
        super(FedoraImageResult, self).__init__(cid, *args, **kwargs)
        self.filename = filename
        # when we have an image, item is always the filename
        self.extradata.update({
            'item': filename,
        })

    @cached_property
    def ffrel(self):
        """Cached instance of fedfind release object."""
        return fedfind.release.get_release(cid=self.cid)

    @cached_property
    def ffimg(self):
        """Cached instance of fedfind image dict."""
        try:
            # this just gets the first image found by the expression,
            # we expect there to be maximum one (per dgilmore, image
            # filenames are unique at least until koji namespacing)
            return next(_img for _img in self.ffrel.all_images if _img['path'].endswith(self.filename))
        except StopIteration:
            # this happens if the expression find *no* images
            raise ValueError("Can't find image {0} in release {1}".format(self.filename, self.cid))

    def default_extradata(self):
        """Populate extradata from compose ID and filename."""
        super(FedoraImageResult, self).default_extradata()
        extradata = {
            'productmd.image.arch': self.ffimg['arch'],
            'productmd.image.disc_number': str(self.ffimg['disc_number']),
            'productmd.image.format': self.ffimg['format'],
            'productmd.image.subvariant': self.ffimg['subvariant'],
            'productmd.image.type': self.ffimg['type'],
        }
        extradata.update(self.extradata)
        self.extradata = extradata

    def default_groups(self):
        """Add to generic result group for this image."""
        super(FedoraImageResult, self).default_groups()
        imgid = '.'.join((self.ffimg['subvariant'], self.ffimg['type'], self.ffimg['format'],
                          self.ffimg['arch'], str(self.ffimg['disc_number']))).lower()
        self.add_group('image', imgid)
        if self.source:
            # We cannot easily do a URL here, unless we start having
            # a store of 'known' sources and how URLs are built for
            # them, or using callbacks, or something. I think we might
            # just ask downstreams to get the group from the group
            # list and add the URL to it?
            self.add_group(self.source, imgid)

# vim: set textwidth=120 ts=8 et sw=4:
