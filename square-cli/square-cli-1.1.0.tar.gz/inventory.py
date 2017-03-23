#!/usr/bin/env python
# coding: utf-8

import json
import optparse
import os
import sys
import traceback
import urllib
import urlparse

import requests


VERSION = "1.0.0"


class InventoryScript(object):
    """ API Ansible Dynamic Inventory

    Gets data from REST API
    """
    def __init__(self, **options):
        self.options = options

    def get_data(self):
        parts = urlparse.urlsplit(self.base_url)

        port = parts.port or (443 if parts.scheme == 'https' else 80)

        url = urlparse.urlunsplit(
            [parts.scheme, '%s:%d' % (parts.hostname, port),
             parts.path, parts.query, parts.fragment])

        url_path = '/api/environments/{}/inventory'.format(self.environment_id)

        q = {}
        if self.show_all:
            q['all'] = 1

        if self.hostname:
            q['host'] = self.hostname

        elif self.hostvars:
            q['hostvars'] = 1

        url_path += '?%s' % urllib.urlencode(q)
        url = urlparse.urljoin(url, url_path)
        response = requests.get(url)
        response.raise_for_status()
        sys.stdout.write(json.dumps(json.loads(response.content),
                                    indent=self.indent) + '\n')

    def run(self):
        try:
            self.base_url = (self.options.get('base_url', '') or
                             os.getenv('REST_API_URL', ''))

            if not self.base_url:
                raise ValueError('No REST API URL specified')

            try:
                # Command line argument takes precedence over environment
                # variable.
                self.environment_id = (
                    int(self.options.get('environment_id', 0) or
                        os.getenv('ENVIRONMENT_ID', 0)))

            except ValueError:
                raise ValueError('Environment ID must be an integer')

            if not self.environment_id:
                raise ValueError('No environment ID specified')

            self.hostname = str(self.options.get('hostname', '') or
                                os.getenv('HOSTNAME', ''))
            self.list_ = bool(self.options.get('list', False) or
                              os.getenv('LIST', ''))
            self.hostvars = bool(self.options.get('hostvars', False) or
                                 os.getenv('INVENTORY_HOSTVARS', ''))
            self.show_all = bool(self.options.get('show_all', False) or
                                 os.getenv('INVENTORY_ALL', ''))
            self.indent = self.options.get('indent', None)
            if self.list_ and self.hostname:
                raise RuntimeError('Only --list or --host may be specified')
            elif self.list_ or self.hostname:
                self.get_data()
            else:
                raise RuntimeError('Either --list or --host must be specified')
        except Exception, e:
            sys.stdout.write('%s\n' % json.dumps(dict(failed=True)))
            if self.options.get('traceback', False):
                sys.stderr.write(traceback.format_exc())
            else:
                sys.stderr.write('%s\n' % str(e))
            if hasattr(e, 'response'):
                sys.stderr.write('%s\n' % e.response.content)
            sys.exit(1)


def main():
    parser = optparse.OptionParser()

    parser.add_option('--traceback', action='store_true',
                      help='Raise on exception on error')

    parser.add_option('-u', '--url', dest='base_url', default='',
                      help='Base URL to access REST API, including username '
                           'and password for authentication (can also be '
                           'specified using REST_API_URL environment '
                           'variable)')

    parser.add_option('-e', '--environemnt', dest='environment_id', type='int',
                      default=0, help='Environment ID (can also be specified '
                                      'using ENVIRONMENT_ID environment v'
                                      'ariable)')

    parser.add_option('--list', action='store_true', dest='list',
                      default=False, help='Return JSON hash of host groups. '
                                          'LIST environment can be specified')

    parser.add_option('--hostvars', action='store_true', dest='hostvars',
                      default=False, help='Return hostvars inline with --list,'
                                          ' under ["_meta"]["hostvars"]. '
                                          'Can also be specified using '
                                          'INVENTORY_HOSTVARS environment '
                                          'variable.')

    parser.add_option('--all', action='store_true', dest='show_all',
                      default=False, help='Return all hosts, including those '
                                          'marked as offline/disabled. '
                                          'Can also be specified '
                                          'using INVENTORY_ALL environment '
                                          'variable.')

    parser.add_option('--host', dest='hostname', default='',
                      help='Return JSON hash of host vars.'
                           'Can also be specified using HOSTNAME '
                           'environment variable.')
    parser.add_option('--indent', dest='indent', type='int', default=None,
                      help='Indentation level for pretty printing output')

    options, args = parser.parse_args()

    InventoryScript(**vars(options)).run()

if __name__ == '__main__':
    main()
