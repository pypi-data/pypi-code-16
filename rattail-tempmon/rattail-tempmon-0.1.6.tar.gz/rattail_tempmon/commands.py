# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tempmon commands
"""

from __future__ import unicode_literals, absolute_import

from rattail.commands import Subcommand


class TempmonClient(Subcommand):
    """
    Manage the tempmon-client daemon
    """
    name = 'tempmon-client'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start daemon")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop daemon")
        stop.set_defaults(subcommand='stop')

        parser.add_argument('-p', '--pidfile',
                            help="Path to PID file.", metavar='PATH')
        parser.add_argument('-D', '--daemonize', action='store_true',
                            help="Daemonize when starting.")

    def run(self, args):
        from rattail_tempmon.client import make_daemon

        daemon = make_daemon(self.config, args.pidfile)
        if args.subcommand == 'start':
            daemon.start(args.daemonize)
        elif args.subcommand == 'stop':
            daemon.stop()


class TempmonServer(Subcommand):
    """
    Manage the tempmon-server daemon
    """
    name = 'tempmon-server'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start daemon")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop daemon")
        stop.set_defaults(subcommand='stop')

        parser.add_argument('-p', '--pidfile',
                            help="Path to PID file.", metavar='PATH')
        parser.add_argument('-D', '--daemonize', action='store_true',
                            help="Daemonize when starting.")

    def run(self, args):
        from rattail_tempmon.server import make_daemon

        daemon = make_daemon(self.config, args.pidfile)
        if args.subcommand == 'start':
            daemon.start(args.daemonize)
        elif args.subcommand == 'stop':
            daemon.stop()
