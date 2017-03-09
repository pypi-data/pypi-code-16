# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from c2.patch.sharesettingcopy.testing import C2_PATCH_SHARESETTINGCOPY_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that c2.patch.sharesettingcopy is properly installed."""

    layer = C2_PATCH_SHARESETTINGCOPY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if c2.patch.sharesettingcopy is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('c2.patch.sharesettingcopy'))

    def test_browserlayer(self):
        """Test that IC2PatchSharesettingcopyLayer is registered."""
        from c2.patch.sharesettingcopy.interfaces import IC2PatchSharesettingcopyLayer
        from plone.browserlayer import utils
        self.assertIn(IC2PatchSharesettingcopyLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = C2_PATCH_SHARESETTINGCOPY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['c2.patch.sharesettingcopy'])

    def test_product_uninstalled(self):
        """Test if c2.patch.sharesettingcopy is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled('c2.patch.sharesettingcopy'))
