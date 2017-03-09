from pyalsi.hardware.disks.disk import Disk, DiskGroup
from nose.plugins.attrib import attr

from pyalsi.tests.base_test import BaseTest
from pyalsi.utils.strings import Colors


@attr('small', 'hardware', 'unit', 'disk')
class TestDiskUnit(BaseTest):

    def test_diskgroup(self):
        Colors.colors['c2'] = ''
        haz_root = False
        group = DiskGroup()
        self.assertIsInstance(group, DiskGroup)
        self.assertIsInstance(group.disks, list)
        for disk in group.disks:
            self.assertIsInstance(disk, Disk)
            if disk.name == 'Root':
                haz_root = True
            self.assertIn('G', disk.to_info_string())
        self.assertTrue(haz_root)
