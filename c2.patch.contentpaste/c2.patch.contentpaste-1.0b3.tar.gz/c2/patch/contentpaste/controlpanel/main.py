
from zope.component import getUtility
from z3c.form import interfaces as z3cinterfaces
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFCore.utils import getToolByName

from c2.patch.contentpaste.controlpanel.interfaces import IContentPasteControlPanel
from c2.patch.contentpaste import ContentPasteMessageFactory as _

class ContentPasteControlPanelEditForm(controlpanel.RegistryEditForm):

    schema = IContentPasteControlPanel
    label = _(u"ContentPaste settings")

    def updateFields(self):
        super(ContentPasteControlPanelEditForm, self).updateFields()

    def updateWidgets(self):
        super(ContentPasteControlPanelEditForm, self).updateWidgets()


class ContentPasteControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ContentPasteControlPanelEditForm
