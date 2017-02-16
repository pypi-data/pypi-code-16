# Copyright (C) Red Hat Inc.
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

"""The core Result class lives here."""

from __future__ import unicode_literals
from __future__ import print_function

# stdlib imports
import logging

# internal imports
from . import helpers

# pylint:disable=invalid-name
logger = logging.getLogger(__name__)

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
        self.conventions = ['result']

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
        """Produce and include or update the meta.conventions item,
        listing the conventions the result complies with. If we have a
        source, add it too.
        """
        # this is called meta.conventions because it's metametadata:
        # it's information about the metadata...
        self.extradata['meta.conventions'] = ' '.join(self.conventions)
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
        the UUID is created from those values in a kinda agreed-upon
        way. Any extra params for the group can be passed in. If there
        is already a group with the same namespace and name, its dict
        will be updated with the passed extraparams; this lets you
        modify an existing group by calling add_group again with the
        same namespace and group_name.
        """
        uuidns = helpers.uuid_namespace(namespace)
        groupdict = {
            'uuid': str(helpers.uuid_namespace(group_name, uuidns)),
            'description': '.'.join((namespace, group_name))
        }
        groupdict.update(**extraparams)
        for curgroup in self.groups:
            try:
                if curgroup['description'] == groupdict['description']:
                    curgroup.update(**extraparams)
                    return
            except TypeError:
                # this is what we get if curgroup is a str not a dict
                pass
        # only get here if no existing group matches
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

# vim: set textwidth=120 ts=8 et sw=4:
