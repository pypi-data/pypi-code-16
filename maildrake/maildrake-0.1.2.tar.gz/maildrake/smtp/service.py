# maildrake/smtp/service.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Run-time SMTP service definition for Mail Drake. """

import argparse
import asyncore
import os
import os.path
import sys

from .. import config
from .. import _metadata
import maildrake.smtp


DEFAULT_ADDRESS = config.ServerAddress(host='localhost', port=25)


class ArgumentParser(argparse.ArgumentParser):
    """ Command-line argument parser for this application. """

    def __init__(self, *args, **kwargs):
        """ Initialise this instance. """
        if 'description' not in kwargs:
            kwargs['description'] = "Mail Drake SMTP server"

        super().__init__(*args, **kwargs)

        self.address_default = "{address.host}:{address.port}".format(
                address=DEFAULT_ADDRESS)

        self.setup_arguments()

    def setup_arguments(self):
        """ Set up arguments special to this program. """
        self.add_argument(
            'address',
            nargs='?',
            help=(
                "local address to bind for this server"
                " as HOST:PORT"
                " (default %(default)s)"
                ),
            )
        self.add_argument(
            '--version',
            action='version',
            version="%(prog)s {version}".format(
                version=_metadata.version_text),
            help="emit the program version, then exit")


def make_address_from_address_argument(text):
    """ Make a `ServerAddress` value from a command-line argument `text`. """
    (host, port) = text.split(":")
    address = config.ServerAddress(host=host, port=int(port))

    return address


class SMTPApplication:
    """ Mail Drake SMTP service application. """

    def parse_commandline(self, argv):
        """ Parse the command line for this application.

            :param argv: Sequence of command-line arguments used to
                invoke this application.
            :return: ``None``.

            The parsed argument collection is set on the `args`
            attribute of this application.

            """
        command_args = list(argv)
        command_path = command_args.pop(0)
        command_name = os.path.basename(command_path)

        parser = ArgumentParser(prog=command_name)
        self.args = parser.parse_args(command_args)

        self.address = make_address_from_address_argument(self.args.address)

    def run(self):
        """ Run this application instance. """
        maildrake.smtp.SMTPServer(localaddr=self.address)
        asyncore.loop()


def main(argv=None):
    """ Run the Mail Drake SMTP service.

        :param argv: Sequence of command-line arguments used to invoke
            this process. Default: `sys.argv`.
        :return: Exit status (integer) for this process.

        """
    if argv is None:
        argv = sys.argv

    exit_status = os.EX_OK

    app = SMTPApplication()

    try:
        app.parse_commandline(argv)
        app.run()

    except SystemExit as exc:
        exit_status = exc.code

    return exit_status


# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.AGPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
