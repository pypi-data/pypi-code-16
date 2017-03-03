from __future__ import absolute_import
import unittest
from commonconf.backends import use_configparser_backend
from commonconf import settings, override_settings
import os

my_dir = os.path.dirname(__file__)
config_path = os.path.join(my_dir, "files", "sections.cfg")


class TestOverrides(unittest.TestCase):
    def test_decorator(self):
        use_configparser_backend(config_path, "Section1")
        self.assertTrue(settings.DEBUG)

        with self.assertRaises(Exception):
            settings.OTHER

        @override_settings(DEBUG="What!", OTHER="Also")
        def get_overridden():
            return settings.DEBUG, settings.OTHER

        debug, other = get_overridden()
        self.assertEquals(debug, "What!")
        self.assertEquals(other, "Also")

        self.assertTrue(settings.DEBUG)

        with self.assertRaises(Exception):
            settings.OTHER

    def test_context(self):
        use_configparser_backend(config_path, "Section1")
        self.assertTrue(settings.DEBUG)

        with self.assertRaises(Exception):
            settings.OTHER

        with override_settings(DEBUG="What!", OTHER="Also"):
            debug = settings.DEBUG
            other = settings.OTHER

        self.assertEquals(debug, "What!")
        self.assertEquals(other, "Also")

        self.assertTrue(settings.DEBUG)

        with self.assertRaises(Exception):
            settings.OTHER


@override_settings(DEBUG="class level", OTHER="More")
class TestClassOverride(unittest.TestCase):
    def test_it(self):
        self.assertEquals(settings.DEBUG, "class level")
        self.assertEquals(settings.OTHER, "More")

    def test_bad_superclass(self):
        with self.assertRaises(Exception):
            @override_settings()
            class BadWrap(object):
                pass
