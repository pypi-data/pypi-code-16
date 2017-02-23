from __future__ import absolute_import
import unittest
from commonconf.backends import use_django_backend
from commonconf import settings

has_django = False
try:
    from django.conf import settings
    v = settings.DEBUG
    has_django = True
except Exception as ex:
    pass


class TestDjangoBackend(unittest.TestCase):
    @unittest.skipUnless(has_django, "Requires Django")
    def test_valid(self):
        use_django_backend()

        value = settings.DEBUG

    @unittest.skipUnless(has_django, "Requires Django")
    def test_invalid(self):
        use_django_backend()
        with self.assertRaises(Exception):
            settings.MISSING_KEY_FOR_TESTING

    @unittest.skipUnless(has_django, "Requires Django")
    def test_default_value(self):
        use_django_backend()

        value = getattr(settings, "MISSING_KEY_FOR_TESTING", "OK")
        self.assertEquals(value, "OK")
