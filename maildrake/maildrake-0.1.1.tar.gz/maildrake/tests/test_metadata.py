# tests/test_metadata.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for `_metadata` private module. """

import collections
import errno
import functools
import json
import re
import unittest.mock
import urllib.parse

import pkg_resources
import testscenarios
import testtools
import testtools.helpers
import testtools.matchers

import maildrake._metadata as metadata


class HasAttribute(testtools.matchers.Matcher):
    """ A matcher to assert an object has a named attribute. """

    def __init__(self, name):
        self.attribute_name = name

    def match(self, instance):
        """ Assert the object `instance` has an attribute named `name`. """
        result = None
        if not testtools.helpers.safe_hasattr(instance, self.attribute_name):
            result = AttributeNotFoundMismatch(instance, self.attribute_name)
        return result


class AttributeNotFoundMismatch(testtools.matchers.Mismatch):
    """ The specified instance does not have the named attribute. """

    def __init__(self, instance, name):
        self.instance = instance
        self.attribute_name = name

    def describe(self):
        """ Emit a text description of this mismatch. """
        text = (
                "{instance!r}"
                " has no attribute named {name!r}").format(
                    instance=self.instance, name=self.attribute_name)
        return text


class metadata_value_TestCase(
        testscenarios.WithScenarios,
        testtools.TestCase):
    """ Test cases for metadata module values. """

    expected_str_attributes = set([
            'version_info',
            'version_text',
            'author',
            'copyright',
            'license',
            'url',
            ])

    scenarios = [
            (name, {'attribute_name': name})
            for name in expected_str_attributes]
    for (name, params) in scenarios:
        if name == 'version_info':
            params['expected_type'] = tuple
            continue
        params['expected_type'] = str

    def test_module_has_attribute(self):
        """ Metadata should have expected value as a module attribute. """
        self.assertThat(
                metadata, HasAttribute(self.attribute_name))

    def test_module_attribute_has_type(self):
        """ Metadata value should be an instance of expected type. """
        instance = getattr(metadata, self.attribute_name)
        self.assertIsInstance(instance, self.expected_type)


class YearRange_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for ‘YearRange’ class. """

    scenarios = [
            ('simple', {
                'begin_year': 1970,
                'end_year': 1979,
                'expected_text': "1970–1979",
                }),
            ('same year', {
                'begin_year': 1970,
                'end_year': 1970,
                'expected_text': "1970",
                }),
            ('no end year', {
                'begin_year': 1970,
                'end_year': None,
                'expected_text': "1970",
                }),
            ]

    def setUp(self):
        """ Set up test fixtures. """
        super(YearRange_TestCase, self).setUp()

        self.test_instance = metadata.YearRange(
                self.begin_year, self.end_year)

    def test_text_representation_as_expected(self):
        """ Text representation should be as expected. """
        result = str(self.test_instance)
        self.assertEqual(result, self.expected_text)


FakeYearRange = collections.namedtuple('FakeYearRange', ['begin', 'end'])

@unittest.mock.patch.object(metadata, 'YearRange', new=FakeYearRange)
class make_year_range_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for ‘make_year_range’ function. """

    scenarios = [
            ('simple', {
                'begin_year': "1970",
                'end_date': "1979-01-01",
                'expected_range': FakeYearRange(begin=1970, end=1979),
                }),
            ('same year', {
                'begin_year': "1970",
                'end_date': "1970-01-01",
                'expected_range': FakeYearRange(begin=1970, end=1970),
                }),
            ('no end year', {
                'begin_year': "1970",
                'end_date': None,
                'expected_range': FakeYearRange(begin=1970, end=None),
                }),
            ('end date UNKNOWN token', {
                'begin_year': "1970",
                'end_date': "UNKNOWN",
                'expected_range': FakeYearRange(begin=1970, end=None),
                }),
            ('end date FUTURE token', {
                'begin_year': "1970",
                'end_date': "FUTURE",
                'expected_range': FakeYearRange(begin=1970, end=None),
                }),
            ]

    def test_result_matches_expected_range(self):
        """ Result should match expected YearRange. """
        result = metadata.make_year_range(self.begin_year, self.end_date)
        self.assertEqual(result, self.expected_range)


class metadata_content_TestCase(testtools.TestCase):
    """ Test cases for content of metadata. """

    def test_copyright_formatted_correctly(self):
        """ Copyright statement should be formatted correctly. """
        regex_pattern = (
                "Copyright © "
                "\d{4}"  # Four-digit year.
                "(?:–\d{4})?"  # Optional range dash and four-digit year.
                )
        regex_flags = re.UNICODE
        self.assertThat(
                metadata.copyright,
                testtools.matchers.MatchesRegex(regex_pattern, regex_flags))

    def test_author_formatted_correctly(self):
        """ Author information should be formatted correctly. """
        regex_pattern = (
                ".+ "  # Name.
                "<[^>]+>"  # Email address, in angle brackets.
                )
        regex_flags = re.UNICODE
        self.assertThat(
                metadata.author,
                testtools.matchers.MatchesRegex(regex_pattern, regex_flags))

    def test_copyright_contains_author(self):
        """ Copyright information should contain author information. """
        self.assertThat(
                metadata.copyright,
                testtools.matchers.Contains(metadata.author))

    def test_url_parses_correctly(self):
        """ Homepage URL should parse correctly. """
        result = urllib.parse.urlparse(metadata.url)
        self.assertIsInstance(
                result, urllib.parse.ParseResult,
                "URL value {url!r} did not parse correctly".format(
                    url=metadata.url))


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
