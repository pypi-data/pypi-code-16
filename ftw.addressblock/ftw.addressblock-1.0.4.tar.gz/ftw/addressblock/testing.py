from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing.mailing import Mailing
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import ploneSite
from plone.testing import z2
from zope.configuration import xmlconfig
import ftw.addressblock.tests.builders


class FtwLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.simplelayout.contenttypes:default')
        applyProfile(portal, 'ftw.addressblock:default')
        applyProfile(portal, 'ftw.addressblock.geo:default')
        applyProfile(portal, 'ftw.addressblock.contact:default')
        applyProfile(portal, 'ftw.subsite:default')

    def testSetUp(self):
        super(FtwLayer, self).testSetUp()
        with ploneSite() as portal:
            Mailing(portal).set_up()

    def testTearDown(self):
        super(FtwLayer, self).testTearDown()
        with ploneSite() as portal:
            Mailing(portal).tear_down()


FTW_FIXTURE = FtwLayer()
FTW_FUNCTIONAL = FunctionalTesting(
    bases=(
        FTW_FIXTURE,
        set_builder_session_factory(functional_session_factory)
    ),
    name='ftw.addressblock:functional'
)
