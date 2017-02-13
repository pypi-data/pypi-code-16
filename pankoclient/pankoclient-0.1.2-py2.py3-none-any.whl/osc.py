# Copyright 2014 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""OpenStackClient plugin for Telemetry Event service."""

from osc_lib import utils


DEFAULT_EVENT_API_VERSION = '2'
API_VERSION_OPTION = 'os_event_api_version'
API_NAME = "event"
API_VERSIONS = {
    "2": "pankoclient.v2.client.Client",
}


def make_client(instance):
    """Returns an queues service client."""
    version = instance._api_version[API_NAME]
    try:
        version = int(version)
    except ValueError:
        version = float(version)

    panko_client = utils.get_client_class(
        API_NAME,
        version,
        API_VERSIONS)
    # NOTE(sileht): ensure setup of the session is done
    instance.setup_auth()
    return panko_client(session=instance.session)


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        '--os-event-api-version',
        metavar='<event-api-version>',
        default=utils.env(
            'OS_EVENT_API_VERSION',
            default=DEFAULT_EVENT_API_VERSION),
        help=('Queues API version, default=' +
              DEFAULT_EVENT_API_VERSION +
              ' (Env: OS_EVENT_API_VERSION)'))
    return parser
