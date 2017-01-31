# Copyright(c) 2016 Nippon Telegraph and Telephone Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

from masakariclient.common.i18n import _
from masakariclient.common import utils


def add_global_args(parser, version):
    # GLOBAL ARGUMENTS
    parser.add_argument(
        '-h', '--help', action='store_true',
        help=argparse.SUPPRESS)

    parser.add_argument(
        '--masakari-api-version', action='version', version=version,
        default=utils.env('MASAKARI_API_VERSION', default='1'),
        help=_('Version number for Masakari API to use, Default to "1".'))

    parser.add_argument(
        '--debug', default=False, action='store_true',
        help=_('Print debugging output.'))


def add_global_identity_args(parser):
    parser.add_argument(
        '--os-auth-plugin', dest='auth_plugin', metavar='AUTH_PLUGIN',
        default=utils.env('OS_AUTH_PLUGIN', default=None),
        help=_('Authentication plugin, default to env[OS_AUTH_PLUGIN]'))

    parser.add_argument(
        '--os-auth-url', dest='auth_url', metavar='AUTH_URL',
        default=utils.env('OS_AUTH_URL'),
        help=_('Defaults to env[OS_AUTH_URL]'))

    parser.add_argument(
        '--os-project-id', dest='project_id', metavar='PROJECT_ID',
        default=utils.env('OS_PROJECT_ID'),
        help=_('Defaults to env[OS_PROJECT_ID].'))

    parser.add_argument(
        '--os-project-name', dest='project_name', metavar='PROJECT_NAME',
        default=utils.env('OS_PROJECT_NAME'),
        help=_('Defaults to env[OS_PROJECT_NAME].'))

    parser.add_argument(
        '--os-tenant-id', dest='tenant_id', metavar='TENANT_ID',
        default=utils.env('OS_TENANT_ID'),
        help=_('Defaults to env[OS_TENANT_ID].'))

    parser.add_argument(
        '--os-tenant-name', dest='tenant_name', metavar='TENANT_NAME',
        default=utils.env('OS_TENANT_NAME'),
        help=_('Defaults to env[OS_TENANT_NAME].'))

    parser.add_argument(
        '--os-domain-id', dest='domain_id', metavar='DOMAIN_ID',
        default=utils.env('OS_DOMAIN_ID'),
        help=_('Domain ID for scope of authorization, defaults to '
               'env[OS_DOMAIN_ID].'))

    parser.add_argument(
        '--os-domain-name', dest='domain_name', metavar='DOMAIN_NAME',
        default=utils.env('OS_DOMAIN_NAME'),
        help=_('Domain name for scope of authorization, defaults to '
               'env[OS_DOMAIN_NAME].'))

    parser.add_argument(
        '--os-project-domain-id', dest='project_domain_id',
        metavar='PROJECT_DOMAIN_ID',
        default=utils.env('OS_PROJECT_DOMAIN_ID'),
        help=_('Project domain ID for scope of authorization, defaults to '
               'env[OS_PROJECT_DOMAIN_ID].'))

    parser.add_argument(
        '--os-project-domain-name', dest='project_domain_name',
        metavar='PROJECT_DOMAIN_NAME',
        default=utils.env('OS_PROJECT_DOMAIN_NAME'),
        help=_('Project domain name for scope of authorization, defaults to '
               'env[OS_PROJECT_DOMAIN_NAME].'))

    parser.add_argument(
        '--os-user-domain-id', dest='user_domain_id',
        metavar='USER_DOMAIN_ID',
        default=utils.env('OS_USER_DOMAIN_ID'),
        help=_('User domain ID for scope of authorization, defaults to '
               'env[OS_USER_DOMAIN_ID].'))

    parser.add_argument(
        '--os-user-domain-name', dest='user_domain_name',
        metavar='USER_DOMAIN_NAME',
        default=utils.env('OS_USER_DOMAIN_NAME'),
        help=_('User domain name for scope of authorization, defaults to '
               'env[OS_USER_DOMAIN_NAME].'))

    parser.add_argument(
        '--os-username', dest='username', metavar='USERNAME',
        default=utils.env('OS_USERNAME'),
        help=_('Defaults to env[OS_USERNAME].'))

    parser.add_argument(
        '--os-user-id', dest='user_id', metavar='USER_ID',
        default=utils.env('OS_USER_ID'),
        help=_('Defaults to env[OS_USER_ID].'))

    parser.add_argument(
        '--os-password', dest='password', metavar='PASSWORD',
        default=utils.env('OS_PASSWORD'),
        help=_('Defaults to env[OS_PASSWORD]'))

    parser.add_argument(
        '--os-trust-id', dest='trust_id', metavar='TRUST_ID',
        default=utils.env('OS_TRUST_ID'),
        help=_('Defaults to env[OS_TRUST_ID]'))

    verify_group = parser.add_mutually_exclusive_group()

    verify_group.add_argument(
        '--os-cacert', dest='verify', metavar='CA_BUNDLE_FILE',
        default=utils.env('OS_CACERT', default=True),
        help=_('Path of CA TLS certificate(s) used to verify the remote '
               'server\'s certificate. Without this option masakari looks '
               'for the default system CA certificates.'))

    verify_group.add_argument(
        '--verify',
        action='store_true',
        help=_('Verify server certificate (default)'))

    verify_group.add_argument(
        '--insecure', dest='verify', action='store_false',
        help=_('Explicitly allow masakariclient to perform "insecure SSL" '
               '(HTTPS) requests. The server\'s certificate will not be '
               'verified against any certificate authorities. This '
               'option should be used with caution.'))

    parser.add_argument(
        '--os-token', dest='token', metavar='TOKEN',
        default=utils.env('OS_TOKEN', default=None),
        help=_('A string token to bootstrap the Keystone database, defaults '
               'to env[OS_TOKEN]'))

    parser.add_argument(
        '--os-access-info', dest='access_info', metavar='ACCESS_INFO',
        default=utils.env('OS_ACCESS_INFO'),
        help=_('Access info, defaults to env[OS_ACCESS_INFO]'))
