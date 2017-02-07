#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the command line interface
"""

import os
import unittest
import unittest.mock

import click.testing

import botman.cli

# pylint: disable=too-few-public-methods
class CliRunnerMixin(object):
    """
    Test case mixin for adding CLI runner support
    """

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Sets up the CLI runner
        """

        super().setUp()

        self.cli_runner = click.testing.CliRunner()
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods

class TestCommand(CliRunnerMixin, unittest.TestCase):
    """
    Tests for the main command
    """

    def setUp(self):
        super().setUp()

        # Ensure that env does not contain our auth_token
        self.initial_auth_token = os.environ.get('BOTMAN_AUTH_TOKEN')
        if self.initial_auth_token is not None:
            del os.environ['BOTMAN_AUTH_TOKEN']

        self.auth_token = 'deadbeef'
        self.bot_patch = unittest.mock.patch('botman.bot.BotmanBot')
        self.mock_bot = self.bot_patch.start()

    def tearDown(self):
        super().tearDown()

        self.bot_patch.stop()

        # Restore the environment variables we might have changed
        if self.initial_auth_token is not None:
            os.environ['BOTMAN_AUTH_TOKEN'] = self.initial_auth_token

    def test_help_message(self):
        """
        Tests that can get the help message
        """

        result = self.cli_runner.invoke(botman.cli.main, ['--help'])
        self.assertEqual(
            0,
            result.exit_code,
            'Command exitted successfully',
        )

        self.assertIn(
            '--help  Show this message and exit.',
            result.output,
            'Help message contained the correct information',
        )

    def test_no_args(self):
        """
        Tests that the command fails when not given an auth token
        """

        result = self.cli_runner.invoke(botman.cli.main)

        self.assertEqual(
            2,
            result.exit_code,
            'Command failed to start correctly',
        )

        self.assertIn(
            'Error: Missing argument "auth_token"',
            result.output,
            'A helpful error message was given',
        )

    def test_auth_token_arg(self):
        """
        Tests that we can provide the auth token as an argument
        """

        result = self.cli_runner.invoke(botman.cli.main, [self.auth_token])

        self.assertEqual(
            0,
            result.exit_code,
            'Command exitted successfully',
        )

        self.assertIn(
            f'Auth token: {self.auth_token}',
            result.output,
            'Command output matched the expected',
        )

        self.mock_bot.assert_called_with(self.auth_token)

    def test_auth_token_env(self):
        """
        Tests that we can provide the auth token as an environment variable
        """

        result = self.cli_runner.invoke(
            botman.cli.main,
            env={'BOTMAN_AUTH_TOKEN': self.auth_token},
        )

        self.assertEqual(
            0,
            result.exit_code,
            'Command exitted successfully',
        )

        self.assertIn(
            f'Auth token: {self.auth_token}',
            result.output,
            'Command output matched the expected',
        )

