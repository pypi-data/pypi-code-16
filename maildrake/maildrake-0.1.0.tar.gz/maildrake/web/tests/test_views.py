# maildrake/web/tests/test_views.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for Flask application views. """

import textwrap
import unittest

import maildrake.web
import maildrake.store
from ...tests.test_store import (
        setup_database,
        teardown_database,
        )


def setup_flask_app(testcase, app):
    """ Set up the Flask application `app` for the `testcase`. """
    app.config['TESTING'] = True
    app.config['DATABASE'] = testcase.db_filename

    testcase.client = app.test_client()


class MailDrakeAppFixture:
    """ Flask app fixture behaviour for MailDrake app test cases. """

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()
        setup_database(self)
        setup_flask_app(self, maildrake.web.app)

    def tearDown(self):
        """ Tear down fixtures for this test case. """
        teardown_database(self)
        super().tearDown()


class anonymous_session_TestCase(
        MailDrakeAppFixture,
        unittest.TestCase):
    """ Test cases for Mail Drake app, anonymous access. """

    def test_message_list_empty(self):
        """ Message list should report no entries. """
        response = self.client.get("/messages")
        expected_content = "No messages in the queue now.".encode('utf-8')
        self.assertIn(expected_content, response.data)


class authenticated_session_TestCase(
        MailDrakeAppFixture,
        unittest.TestCase):
    """ Test cases for Mail Drake app, authenticated sessions. """

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        maildrake.web.app.config['USERNAME'] = "architecto"
        maildrake.web.app.config['PASSPHRASE'] = "maxime debitis labore"

    def login(self, username, passphrase):
        """ Log in to a session. """
        response = self.client.post(
                "/login", data={
                    'username': username,
                    'passphrase': passphrase,
                    },
                follow_redirects=True,
                )
        return response

    def logout(self):
        """ Log out of a session. """
        response = self.client.get("/logout", follow_redirects=True)
        return response

    def test_login_get_presents_form(self):
        """ Should present login form when GET request. """
        response = self.client.get("/login", follow_redirects=True)
        expected_content = textwrap.dedent("""\
                <input type="submit" value="Log in">""").encode('utf-8')
        self.assertIn(expected_content, response.data)

    def test_valid_login_accepted(self):
        """ Valid login credentials should be accepted. """
        response = self.login(
                username=maildrake.web.app.config['USERNAME'],
                passphrase=maildrake.web.app.config['PASSPHRASE'],
                )
        expected_content = "You are now logged in.".encode('utf-8')
        self.assertIn(expected_content, response.data)

    def test_valid_login_then_logout_succeeds(self):
        """ Logout from a session should be accepted. """
        self.login(
                username=maildrake.web.app.config['USERNAME'],
                passphrase=maildrake.web.app.config['PASSPHRASE'],
                )
        response = self.logout()
        expected_content = "You are now logged out.".encode('utf-8')
        self.assertIn(expected_content, response.data)

    def test_unknown_username_rejected(self):
        """ Unknown username should be rejected. """
        response = self.login(
                username="repellendus",
                passphrase=maildrake.web.app.config['PASSPHRASE'],
                )
        expected_content = "Invalid username and/or passphrase".encode('utf-8')
        self.assertIn(expected_content, response.data)

    def test_incorrect_passphrase_rejected(self):
        """ Incorrect passphrase should be rejected. """
        response = self.login(
                username=maildrake.web.app.config['USERNAME'],
                passphrase="b0gUs",
                )
        expected_content = "Invalid username and/or passphrase".encode('utf-8')
        self.assertIn(expected_content, response.data)


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
