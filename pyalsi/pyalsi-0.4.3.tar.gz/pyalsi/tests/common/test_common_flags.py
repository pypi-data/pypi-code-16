from pyalsi.tests.base_test import BaseTest
from pyalsi import cli
from pyalsi.logos import logos
from pyalsi.colors import normal, bold
from nose.plugins.attrib import attr
from pyalsi.system.system import System

@attr('common')
class TestCommonCommandFlags(BaseTest):

    @attr('small')
    def test_unflagged_functionality(self):
        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('OS', result.output)

    @attr('medium')
    def test_distro_flag_functionality(self):
        for distro in System().distro_subclass_map.keys():
            result = self.runner.invoke(cli, ['-d', distro])
            self.assertIn(distro, result.output)
            self.assertEqual(result.exit_code, 0)

    @attr('medium')
    def test_logo_flag_functionality(self):
        for distro in System().distro_subclass_map.keys():
            for logo in logos[distro]:
                result = self.runner.invoke(cli, ['-d', distro, '--logo', logo])
                self.assertIn(distro, result.output)
                self.assertEqual(result.exit_code, 0)

    @attr('large')
    def test_colour_flag_functionality(self):
        for n in normal:
            for b in bold:
                result = self.runner.invoke(cli, ['-n', n, '-b', b])
                self.assertEqual(result.exit_code, 0)

    @attr('medium')
    def test_info_below_flag_functionality(self):
        for distro in System().distro_subclass_map.keys():
            result = self.runner.invoke(cli, ['-d', distro, '-l'])
            self.assertNotIn('\tOS', result.output)
