# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import c2.patch.sharesettingcopy


class C2PatchSharesettingcopyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=c2.patch.sharesettingcopy)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'c2.patch.sharesettingcopy:default')


C2_PATCH_SHARESETTINGCOPY_FIXTURE = C2PatchSharesettingcopyLayer()


C2_PATCH_SHARESETTINGCOPY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(C2_PATCH_SHARESETTINGCOPY_FIXTURE,),
    name='C2PatchSharesettingcopyLayer:IntegrationTesting'
)


C2_PATCH_SHARESETTINGCOPY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(C2_PATCH_SHARESETTINGCOPY_FIXTURE,),
    name='C2PatchSharesettingcopyLayer:FunctionalTesting'
)


C2_PATCH_SHARESETTINGCOPY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        C2_PATCH_SHARESETTINGCOPY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='C2PatchSharesettingcopyLayer:AcceptanceTesting'
)
