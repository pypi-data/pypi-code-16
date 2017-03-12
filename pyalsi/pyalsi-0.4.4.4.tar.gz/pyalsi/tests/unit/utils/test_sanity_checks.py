from nose.plugins.attrib import attr

from pyalsi.tests.base_test import BaseTest
from pyalsi.system.system import System
from pyalsi.logos import logos

@attr('small', 'sanity', 'unit')
class TestUtilsUnit(BaseTest):

    def test_systems_in_logos(self):
        for distro in System().distro_subclass_map.keys():
            self.assertIn(distro, logos.keys())
