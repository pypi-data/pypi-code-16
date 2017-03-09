
from zope.component import getUtility
from z3c.form import interfaces as z3cinterfaces
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFCore.utils import getToolByName

from c2.patch.sharesettingcopy.controlpanel.interfaces import IShareSettingCopyControlPanel
from c2.patch.sharesettingcopy import _


class ShareSettingCopyControlPanelEditForm(controlpanel.RegistryEditForm):

    schema = IShareSettingCopyControlPanel
    label = _(u"Share Setting Copy")

    def updateFields(self):
        super(ShareSettingCopyControlPanelEditForm, self).updateFields()

    def updateWidgets(self):
        super(ShareSettingCopyControlPanelEditForm, self).updateWidgets()


class ShareSettingCopyControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ShareSettingCopyControlPanelEditForm
