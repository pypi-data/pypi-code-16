u"""
LICENSE:
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

    kudubot is a chat bot framework. It allows developers to write
    services for arbitrary chat services.

    kudubot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    kudubot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE
"""

from __future__ import absolute_import
import sys
import raven
import logging
import argparse
from kudubot.metadata import version, sentry_dsn
from kudubot.exceptions import InvalidConfigException
from kudubot.connections.Connection import Connection
from kudubot.config.GlobalConfigHandler import GlobalConfigHandler
from itertools import ifilter


def main():  # pragma: no cover
    u"""
    The Main Method of the Program that starts the Connection Listener in accordance with the
    command line arguments

    :return: None
    """

    try:
        args = parse_args()

        # noinspection PyUnresolvedReferences
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
        elif args.verbose:
            logging.basicConfig(level=logging.INFO)

        # noinspection PyUnresolvedReferences
        connection = initialize_connection(args.connection.lower())

        connection.listen()
    except Exception, e:
        sentry = raven.Client(dsn=sentry_dsn, release=version)
        sentry.captureException()
        raise e


def initialize_connection(identifier):  # pragma: no cover
    u"""
    Loads the connection for the specified identifier
    If the connection was not found in the local configuration, the program exits.

    :param identifier: The identifier for the Connection
    :return: The Connection object
    """

    try:
        config_handler = GlobalConfigHandler()
    except InvalidConfigException, e:
        print u"Loading configuration failed:"
        print unicode(e)
        sys.exit(1)

    connections = config_handler.load_connections()
    services = config_handler.load_services()

    try:
        connection_type = list(ifilter(lambda x: x.identifier == identifier, connections))[0]
        return connection_type(services)
    except IndexError:
        print u"Connection Type " + identifier + u" is not implemented or imported using the config file"
        sys.exit(1)
    except InvalidConfigException, e:
        print u"Connection Configuration failed:"
        print unicode(e)
        sys.exit(1)


def parse_args():  # pragma: no cover
    u"""
    Parses the Command Line Arguments using argparse

    :return: The parsed arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(u"connection", help=u"The Type of Connection to use")

    parser.add_argument(u"-v", u"--verbose", action=u"store_true", help=u"Activates verbose output")
    parser.add_argument(u"-d", u"--debug", action=u"store_true", help=u"Activates debug-level logging output")

    return parser.parse_args()
