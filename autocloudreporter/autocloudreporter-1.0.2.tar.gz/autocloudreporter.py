# Copyright (C) Red Hat Inc.
#
# autocloudreporter is free software; you can redistribute it
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

"""fedmsg consumer to report Autocloud results to ResultsDB."""

__version__ = "1.0.2"

from __future__ import unicode_literals
from __future__ import print_function

import fedmsg.consumers
from resultsdb_api import ResultsDBapi, ResultsDBapiException
from resultsdb_conventions.fedora import FedoraImageResult

class AutocloudReporter(fedmsg.consumers.FedmsgConsumer):
    """A fedmsg consumer that consumes Autocloud test results and
    produces ResultsDB results. Listens for production Autocloud
    fedmsgs and reports to the production ResultsDB.
    """
    topic = ["org.fedoraproject.prod.autocloud.image.failed",
             "org.fedoraproject.prod.autocloud.image.success"]
    config_key = "autocloudreporter.prod.enabled"
    # FIXME: this is a bit lazy, we're hardcoding the infra internal
    # hostname for the production server here, because if we use the
    # public hostname, when hitting it from inside infra the request
    # gets looped through the proxy server and is rejected (as rdb
    # just uses IP range auth at the moment). We can't change infra
    # DNS because different hosts serve different bits of taskotron.
    # Once proper auth is implemented for RDB we can change this.
    resultsdb_url = 'http://resultsdb01.qa.fedoraproject.org/resultsdb_api/api/v2.0/'
    autocloud_url = 'https://apps.fedoraproject.org/autocloud'

    def _log(self, level, message):
        """Convenience function for sticking the class name on the
        front of the log message as an identifier.
        """
        logfnc = getattr(self.log, level)
        logfnc("%s: %s", self.__class__.__name__, message)

    def consume(self, message):
        """Consume incoming message."""
        # can't do anything useful without resultsdb
        try:
            rdb_instance = ResultsDBapi(self.resultsdb_url)
        except ResultsDBapiException as err:
            self._log('error', err)
            return

        try:
            job_id = message['body']['msg']['job_id']
            cid = message['body']['msg']['compose_id']
            # bit lazy, assumes no queries
            filename = message['body']['msg']['compose_url'].split('/')[-1]
            outcome = {'success': "PASSED", 'failed': "FAILED"}.get(
                message['body']['msg']['status'], 'NEEDS_INSPECTION')
        except KeyError:
            self._log('error', "Essential information missing from message {0}!".format(
                message['body']['msg_id']))
            return

        self._log('info', "Reporting for {0} job {1}...".format(cid, job_id))
        res = FedoraImageResult(
            cid=cid,
            filename=filename,
            outcome=outcome,
            tc_name='compose.cloud.all',
            ref_url="{0}/jobs/{1}/output".format(self.autocloud_url, job_id),
            tc_url='https://github.com/kushaldas/autocloud/',
            note='',
            source='autocloud'
        )
        try:
            res.report(rdb_instance)
            # note: the above raises an exception if any error occurs,
            # if it does not raise, we can assume reporting worked
            self._log('info', "Reporting for {0} job {1} complete".format(cid, job_id))
        # this is OK, pylint, we just really really don't want fedmsg
        # consumers to crash
        # pylint:disable=broad-except
        except Exception as err:
            self._log('error', "Reporting error! {0}".format(err))

        return


class AutocloudStagingReporter(AutocloudReporter):
    """The staging consumer: listens for staging fedmsgs and reports
    to the staging ResultsDB.
    """
    topic = ["org.fedoraproject.stg.autocloud.image.failed",
             "org.fedoraproject.stg.autocloud.image.success"]
    config_key = "autocloudreporter.stg.enabled"
    resultsdb_url = 'http://resultsdb-stg01.qa.fedoraproject.org/resultsdb_api/api/v2.0/'
    autocloud_url = 'https://apps.stg.fedoraproject.org/autocloud'


class AutocloudTestReporter(AutocloudReporter):
    """The testing consumer: listens for dev messages and by default
    reports to a ResultsDB instance running on localhost (see docs
    for setting up a test local instance).
    """
    topic = ["org.fedoraproject.dev.autocloud.image.failed",
             "org.fedoraproject.dev.autocloud.image.success"]
    config_key = "autocloudreporter.test.enabled"
    resultsdb_url = 'http://localhost:5001/api/v2.0/'
    autocloud_url = 'https://apps.fedoraproject.org/autocloud'
    validate_signatures = False

# vim: set textwidth=100 ts=8 et sw=4:
