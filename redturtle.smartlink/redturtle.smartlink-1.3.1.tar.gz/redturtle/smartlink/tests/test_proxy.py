# -*- coding: utf-8 -*-

import unittest
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig
from redturtle.smartlink.tests.base import TestCase
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class ProxyTestSetup(TestCase):
    """ Testing the proxy feature """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.setRoles(('Manager', ))
        self.smartlink_config = getUtility(
            ISmartlinkConfig, name="smartlink_config"
        )
        self.smartlink_config.proxy_enabled = True
        self.folder.invokeFactory(
            type_name='Link', id='the-link',
            title='Link to something', description='This is a link'
        )
        self.link = self.folder['the-link']
        self.folder.invokeFactory(
            type_name='Document', id='internal-document',
            title='Internal doc', description='This is a document'
        )
        self.doc = self.folder['internal-document']
        self.link.setInternalProxy(True)
        self.link.setInternalLink(self.doc)
        self.link.reindexObject()
        notify(ObjectModifiedEvent(self.link))

    def test_widget_feature_disabled(self):
        self.smartlink_config.proxy_enabled = False
        html = self.link.base_edit()
        self.assertFalse('"internalProxy"' in html)

    def test_widget_feature_enabled(self):
        html = self.link.base_edit()
        self.assertTrue('"internalProxy"' in html)

    def test_linked_ct_attributes(self):
        self.assertEqual(self.link.Title(), self.doc.Title())
        self.assertEqual(self.link.Description(), self.doc.Description())
        # attributes access is not proxied
        self.assertEqual(self.link.title, 'Link to something')

    def test_not_linked_ct_attributes_if_globally_disabled(self):
        self.smartlink_config.proxy_enabled = False
        self.assertEqual(self.link.Title(), "Link to something")
        self.assertEqual(self.link.Description(), "This is a link")

    def test_not_linked_ct_attributes_if_locally_disabled(self):
        self.link.setInternalProxy(False)
        self.assertEqual(self.link.Title(), "Link to something")
        self.assertEqual(self.link.Description(), "This is a link")

    def test_catalog_metadata(self):
        result = self.portal.portal_catalog(portal_type='Link')[0]
        self.assertEqual(result.Title, self.doc.Title())
        self.assertEqual(result.Description, self.doc.Description())

    def test_catalog_index(self):
        results = self.portal.portal_catalog(Title='Internal doc')
        self.assertEqual(len(results), 2)
        results = self.portal.portal_catalog(Description='a document')
        self.assertEqual(len(results), 2)

    def test_catalog_updated_on_change(self):
        self.doc.edit(title="This is a page", description="Foo bar baz")
        self.doc.reindexObject()
        notify(ObjectModifiedEvent(self.doc))
        results = self.portal.portal_catalog(
            Title='a page', portal_type='Link'
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].Title, "This is a page")
        results = self.portal.portal_catalog(
            Description='Foo bar baz', portal_type='Link'
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].Description, "Foo bar baz")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ProxyTestSetup))
    return suite
