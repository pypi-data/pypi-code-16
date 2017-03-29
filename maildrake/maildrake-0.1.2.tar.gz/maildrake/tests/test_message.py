# maildrake/tests/test_message.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit tests for email message format behaviour. """

import datetime
import email
import email.message
import textwrap
import unittest

import testscenarios

import maildrake
import maildrake.message


def make_message_scenarios():
    """ Make message scenarios for test cases. """
    scenarios = [
            ('566b9184556a2e3c12c157a135238290a10c90bd@googlemail.com', {
                'raw_text': textwrap.dedent("""\
                    Message-Id: <566b9184556a2e3c12c157a135238290a10c90bd@googlemail.com>
                    Date: Sun, 01 Jan 2017 00:00:00 +0000
                    From: marshallkevin@gmail.com
                    To: roy10@larson.org.au, stephanierusso@hayes.org.au,
                        ccochran@smith.info, irwinspencer@parker.com
                    Subject: Illo aperiam eum nemo corrupti aut quisquam.

                    Nihil illum ab autem. Cum numquam exercitationem dolores
                    incidunt aspernatur sint. Quos quaerat veniam provident eius.
                    """),
                'message_id': "566b9184556a2e3c12c157a135238290a10c90bd@googlemail.com",
                'message_date_timestamp': datetime.datetime.strptime(
                    "2017-01-01 +0000", "%Y-%m-%d %z"),
                }),
            ('cbd4074ed2d91524590aaa4faf7ffaf8@iis.com.au', {
                'raw_text': textwrap.dedent("""\
                    Message-Id: <cbd4074ed2d91524590aaa4faf7ffaf8@iis.com.au>
                    Date: Mon, 02 Jan 2017 00:00:00 +0000
                    From: hlopez@harris.biz
                    To: monique94@watts.biz, smithmiranda@hotmail.com.au
                    Subject: Odio praesentium nostrum fugit dicta at libero quae.

                    Error facilis eligendi deserunt sit dolorem aliquid debitis.
                    Aperiam hic earum animi quibusdam est omnis. Iusto neque
                    aspernatur quam doloremque.
                    """),
                'message_id': "cbd4074ed2d91524590aaa4faf7ffaf8@iis.com.au",
                'message_date_timestamp': datetime.datetime.strptime(
                    "2017-01-02 +0000", "%Y-%m-%d %z"),
                }),
            ('62551d29a4385e0e0e7679b94c671ef72fdcdbcfb01c61bee93c96b9d5268c71@mail.thompson-hall.edu', {
                'raw_text': textwrap.dedent("""\
                    Message-Id: <62551d29a4385e0e0e7679b94c671ef72fdcdbcfb01c61bee93c96b9d5268c71@mail.thompson-hall.edu>
                    Date: Tue, 03 Jan 2017 00:00:00 +0000
                    From: ryan21@thompson-hall.edu
                    To: juliaharris@hotmail.com
                    Subject: Dolorum deleniti consectetur provident.

                    Qui dolor fugit aliquam repudiandae exercitationem. Beatae
                    deserunt iure neque ab vel. Quisquam provident illo commodi
                    eaque maiores omnis repellat. Dolorum labore hic officia
                    molestias non.
                    """),
                'message_id': "62551d29a4385e0e0e7679b94c671ef72fdcdbcfb01c61bee93c96b9d5268c71@mail.thompson-hall.edu",
                'message_date_timestamp': datetime.datetime.strptime(
                    "2017-01-03 +0000", "%Y-%m-%d %z"),
                }),
            ]

    for (name, scenario) in scenarios:
        scenario['test_message'] = email.message_from_string(
                scenario['raw_text'],
                _class=maildrake.message.Message)

    return scenarios


def make_attrs_dict_from_message(message):
    """ Make a `dict` of message attributes from `message`. """
    attrs = {
            'unixfrom': message.get_unixfrom(),
            'fields': message.items(),
            'is_multipart': message.is_multipart(),
            'content_type': message.get_content_type(),
            'params': message.get_params(),
            'preamble': message.preamble,
            'epilogue': message.epilogue,
            'defects': message.defects,
            }

    return attrs


class WithMessageCompareTestCase(unittest.TestCase):
    """
    A test case that can assert equality of `email.message.Message` instances.
    """

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.addTypeEqualityFunc(
                email.message.Message, self.assertEmailMessageEqual)
        self.addTypeEqualityFunc(
                maildrake.message.Message, self.assertEmailMessageEqual)

    def assertEmailMessageEqual(self, a, b, msg=None):
        """
        Test that two `email.message.Message` instances have the same value.
        """
        message_attrs = {
            message: make_attrs_dict_from_message(message)
            for message in [a, b]}
        error = None
        if message_attrs[a] != message_attrs[b]:
            standard_message = (
                    "Message attributes are different:\n{a}\n{b}"
                    ).format(
                        a=message_attrs[a], b=message_attrs[b])
            self.fail(self._formatMessage(msg, standard_message))


class Message_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for class `Message`. """

    scenarios = make_message_scenarios()

    def test_is_email_message(self):
        """ Should be an `email.message.Message` instance. """
        self.assertIsInstance(self.test_message, email.message.Message)


class Message_message_id_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for property `Message.message_id`. """

    scenarios = make_message_scenarios()

    def test_returns_expected_message_id(self):
        """ Should return expected message ID for “Message-Id” field value. """
        result = self.test_message.message_id
        expected_result = self.message_id
        self.assertEqual(result, expected_result)


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
