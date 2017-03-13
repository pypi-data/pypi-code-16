from nose.plugins.attrib import attr

from pyalsi.tests.base_test import BaseTest
from pyalsi.utils.types import Bytes, Gigabyte, Megabyte


@attr('small', 'hardware', 'unit', 'disk')
class TestUtilsUnit(BaseTest):

    def test_types(self):
        self.assertEqual(Megabyte(1024).to_gigabytes(), 1)
        self.assertEqual(Megabyte(1).to_bytes(), 1048576)
        self.assertEqual(Bytes(1048576).to_megabytes(), 1)
        self.assertEqual(Bytes(1073741824).to_gigabytes(), 1)
        self.assertEqual(Gigabyte(1).to_bytes(), 1073741824)
        self.assertEqual(Gigabyte(1).to_megabytes(), 1024)
