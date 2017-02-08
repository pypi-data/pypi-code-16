# -*- coding: utf-8 -*-
from collective.calltoaction.interfaces import ICollectiveCalltoactionSettings
from collective.calltoaction.testing import COLLECTIVE_CALLTOACTION_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.layout.globals.interfaces import IViewView
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewlet

import unittest


class ViewletTestCase(unittest.TestCase):

    layer = COLLECTIVE_CALLTOACTION_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder = api.content.create(
            container=self.portal, type='Folder', title='Folder')

    def test_viewlet_only_on_view(self):
        # When the view is not on IViewView, the viewlet is not registered.
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        self.assertFalse(IViewView.providedBy(view))
        viewlet_manager = queryMultiAdapter(
            (self.folder, request, view),
            IContentProvider,
            'plone.abovecontentbody')
        viewlet = queryMultiAdapter(
            (self.folder, request, view, viewlet_manager),
            IViewlet,
            'collective.calltoaction')
        self.assertTrue(viewlet is None)

    def test_viewlet(self):
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        alsoProvides(view, IViewView)
        self.assertTrue(IViewView.providedBy(view))
        viewlet_manager = queryMultiAdapter(
            (self.folder, request, view),
            IContentProvider,
            'plone.abovecontentbody')
        viewlet = queryMultiAdapter(
            (self.folder, request, view, viewlet_manager),
            IViewlet,
            'collective.calltoaction')
        self.assertTrue(viewlet is not None)
        viewlet.update()
        # We expect data from the portlet assignment in
        # profiles/testfixture/portlets.xml.
        self.assertEqual(len(viewlet.data), 1)
        portlet = viewlet.data[0]
        self.assertIn('assignment', portlet.keys())
        self.assertIn('html', portlet.keys())
        assignment = portlet['assignment']
        self.assertEqual(assignment.milli_seconds_until_overlay, 1000)
        portlet_html = portlet['html']
        self.assertIn('portletCallToAction', portlet_html)
        self.assertIn('portletCallToAction', portlet_html)
        viewlet_html = viewlet.render()
        self.assertIn(portlet_html, viewlet_html)
        self.assertIn('data-timeout="1000"', viewlet_html)

    def test_portlet_inheritance(self):
        portal = self.layer['portal']
        folder = portal.folder2
        request = folder.REQUEST
        view = folder.restrictedTraverse('@@plone')
        alsoProvides(view, IViewView)
        self.assertTrue(IViewView.providedBy(view))
        viewlet_manager = queryMultiAdapter(
            (folder, request, view),
            IContentProvider,
            'plone.abovecontentbody')
        viewlet = queryMultiAdapter(
            (folder, request, view, viewlet_manager),
            IViewlet,
            'collective.calltoaction')
        self.assertTrue(viewlet is not None)
        viewlet.update()
        # The portlet from the test fixture is blocked.
        self.assertEqual(len(viewlet.data), 0)

        # Show the action globally.  This ignores portlet inheritance.
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ICollectiveCalltoactionSettings, check=False)
        self.assertFalse(settings.show_global)
        settings.show_global = True

        # Now we should see the portlet
        viewlet.update()
        self.assertEqual(len(viewlet.data), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ViewletTestCase))
    return suite
