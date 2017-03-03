# -*- coding: utf-8 -*-
'''Setup tests for this package.'''
from experimental.bwtools.testing import EXPERIMENTAL_BWTOOLS_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    '''Test that experimental.bwtools is properly installed.'''

    layer = EXPERIMENTAL_BWTOOLS_INTEGRATION_TESTING

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        '''Test if experimental.bwtools is installed.'''
        self.assertTrue(self.installer.isProductInstalled(
            'experimental.bwtools'))

    def test_browserlayer(self):
        '''Test that IExperimentalBwtoolsLayer is registered.'''
        from experimental.bwtools.interfaces import (
            IExperimentalBwtoolsLayer)
        from plone.browserlayer import utils
        self.assertIn(IExperimentalBwtoolsLayer, utils.registered_layers())

    def test_registry(self):
        '''Test that the registry records are correctly installed.
        '''
        pr = api.portal.get_tool('portal_registry')
        self.assertIn('experimental.bwtools.known_bad_ips', pr)


class TestUninstall(unittest.TestCase):

    layer = EXPERIMENTAL_BWTOOLS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['experimental.bwtools'])

    def test_product_uninstalled(self):
        '''Test if experimental.bwtools is cleanly uninstalled.'''
        self.assertFalse(self.installer.isProductInstalled(
            'experimental.bwtools'))

    def test_browserlayer_removed(self):
        '''Test that IExperimentalBwtoolsLayer is removed.'''
        from experimental.bwtools.interfaces import \
            IExperimentalBwtoolsLayer
        from plone.browserlayer import utils
        self.assertNotIn(IExperimentalBwtoolsLayer, utils.registered_layers())

    def test_registry_cleaned(self):
        '''Test that the registry records are correctly installed.
        '''
        pr = api.portal.get_tool('portal_registry')
        package_keys = [
            key for key in pr.keys()
            if key.startswith('experimental.bwtools')
        ]
        self.assertListEqual(package_keys, [])
