#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for command parameter handling and parsing
"""

import unittest

import botman.commands.base
import botman.errors

class TestBaseCommandArg(unittest.TestCase):
    """
    Tests for the base command argument implementation
    """

    def test_return_value(self):
        """
        Tests the return value from parsing
        """

        value = 'test value'
        arg_type = botman.commands.base.BaseCommandArg('generic')

        self.assertEqual(
            value,
            arg_type.parse('name', value),
            'The correct value was parsed out',
        )

    def test_default_value(self):
        """
        Tests that the default value is used for no value
        """

        arg_type = botman.commands.base.BaseCommandArg(
            'generic',
            default='default',
        )

        self.assertEqual(
            'default',
            arg_type.parse('name', None),
            'The default value was used for a missing value',
        )

    def test_missing_required(self):
        """
        Tests that an exception is thrown for a missing required value
        """

        arg_type = botman.commands.base.BaseCommandArg(
            'generic',
            required=True,
        )

        expected = 'Missing required parameter: name'
        with self.assertRaises(botman.errors.CommandUsageError, msg=expected):
            arg_type.parse('name', None)

    def test_human_friendly_required(self):
        """
        Tests the output for humanizing a required value
        """

        arg_type = botman.commands.base.BaseCommandArg(
            'generic',
            required=True,
        )

        self.assertEqual(
            'generic (required)',
            arg_type.human_friendly,
            'Humanized required value',
        )

    def test_human_friendly_optional(self):
        """
        Tests the output for humanizing an optional value
        """

        arg_type = botman.commands.base.BaseCommandArg(
            'generic',
        )

        self.assertEqual(
            'generic (optional)',
            arg_type.human_friendly,
            'Humanized optional value',
        )

class TestIntArg(unittest.TestCase):
    """
    Tests for the integer argument type
    """

    def test_positive_int(self):
        """
        Tests that it can parse non-negative integer values
        """

        arg_type = botman.commands.base.IntArg()

        self.assertEqual(
            9001,
            arg_type.parse('test', '9001'),
            'Was able to parse a positive integer',
        )

    def test_negative_int(self):
        """
        Tests that it can parse negative integer values
        """

        arg_type = botman.commands.base.IntArg()

        self.assertEqual(
            -1,
            arg_type.parse('test', '-1'),
            'Was able to parse a negative integer',
        )

    def test_invalid_int(self):
        """
        Tests that non-integer values are not accepted
        """

        arg_type = botman.commands.base.IntArg()

        expected = '"a" is a not a number'
        with self.assertRaises(botman.errors.CommandUsageError, msg=expected):
            arg_type.parse('test', 'a')

