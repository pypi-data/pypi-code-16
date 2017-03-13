from pyalsi.hardware.vga.vga import VgaCard, Pci
from nose.plugins.attrib import attr

from pyalsi.tests.base_test import BaseTest
from pyalsi.utils.strings import Colors
from pyalsi.tests.mock_classes.os_popen import MockOsPopen
from mock import patch


@attr('small', 'hardware', 'unit', 'pci')
class TestVgaUnit(BaseTest):

    def test_vga_vanilla(self):
        pci_devices = Pci.get_vga_devices()
        self.assertIsInstance(pci_devices, list)

    @patch('os.popen', MockOsPopen)
    def test_vga_dual_mocked(self):
        self.assertIn('x2', Pci.get_vga_devices()[0])


