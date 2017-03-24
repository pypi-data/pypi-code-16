# maildrake/smtp/__init__.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Server behaviour for SMTP. """

import email
import logging
import smtpd

import maildrake.message
import maildrake.store.sqlite


__package__ = "maildrake.smtp"

logger = logging.getLogger(__package__)


class SMTPServer(smtpd.SMTPServer):
    """
    Server for SMTP requests.

    The server receives messages on the specified local address, but
    does not pass them on further.

    """

    def __init__(self, localaddr, remoteaddr=None, *args, **kwargs):
        if 'decode_data' not in kwargs:
            kwargs['decode_data'] = True
        super().__init__(localaddr, remoteaddr, *args, **kwargs)

        path = maildrake.store.sqlite.get_database_file_path()
        self._database_file_path = path

        logger.info(
                "SMTP server listening on {addr}".format(
                    addr=localaddr))

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """ Process an incoming message from the client `peer`. """
        logger.info(
                "SMTP connection from {peer}".format(peer=peer))
        connection = maildrake.store.sqlite.connect(self._database_file_path)
        message = email.message_from_string(
                data,
                _class=maildrake.message.Message)
        logger.info(
                "Received message {id}".format(id=message.message_id))
        with connection:
            maildrake.store.sqlite.create_message(connection, message)


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
