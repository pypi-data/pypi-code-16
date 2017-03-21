"""Tests for our main micros CLI module."""


from subprocess import getoutput
from unittest import TestCase

from micros import __version__ as VERSION


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = getoutput('micros -h')
        self.assertTrue('Usage:' in str(output))

        output = getoutput('micros --help')
        self.assertTrue('Usage:' in str(output))


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = getoutput('micros --version')
        self.assertEqual(str(output.strip()), VERSION)

