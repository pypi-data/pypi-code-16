# maildrake/message.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Email message behaviour for Mail Drake. """

import email.message
import re


class Message(email.message.Message):
    """ An email message. """

    message_id_pattern = re.compile("<(?P<message_id>[^>]+)>")

    @property
    def message_id(self):
        """ Get the message ID from the “Message-Id” field value.

            :return: The message ID value.

            The standard for email messages, RFC 5322, defines the
            “Message-Id” field format as representing the field value
            enclosed in angle brackets (‘<’, ‘>’).

            """
        field_value = self['message-id']
        message_id_match = self.message_id_pattern.match(field_value)
        message_id = message_id_match.group('message_id')

        return message_id


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
