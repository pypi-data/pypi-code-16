# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import experimental.bwtools


class ExperimentalBwtoolsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=experimental.bwtools)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'experimental.bwtools:default')


EXPERIMENTAL_BWTOOLS_FIXTURE = ExperimentalBwtoolsLayer()


EXPERIMENTAL_BWTOOLS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EXPERIMENTAL_BWTOOLS_FIXTURE,),
    name='ExperimentalBwtoolsLayer:IntegrationTesting'
)


EXPERIMENTAL_BWTOOLS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EXPERIMENTAL_BWTOOLS_FIXTURE,),
    name='ExperimentalBwtoolsLayer:FunctionalTesting'
)


EXPERIMENTAL_BWTOOLS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        EXPERIMENTAL_BWTOOLS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ExperimentalBwtoolsLayer:AcceptanceTesting'
)
