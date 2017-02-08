from Acquisition import aq_inner, aq_parent, aq_base
from Products.Five.utilities import marker as fivemarker
from z3c.form import form, button
from plone.autoform.form import AutoExtensibleForm
from plone.memoize.view import memoize
from Solgema.RichMenu.interfaces import ISolgemaRichMenuAttributes, ISolgemaRichMenuMarker
from Solgema.RichMenu.browser.content import SolgemaRichMenuControl
from Solgema.RichMenu.config import _

class ManageSolgemaRichMenuAttributes(AutoExtensibleForm, form.EditForm):
    schema = ISolgemaRichMenuAttributes

    form_name = 'richmenu_attributes'
    label = _('Rich Menu parameters')

    def applyChanges(self, data):
        fivemarker.mark(self.context, ISolgemaRichMenuMarker)
        changes = super(ManageSolgemaRichMenuAttributes, self).applyChanges(data)
        aq_inner(self.context).reindexObject()
        return changes

class SolgemaRichMenuControlDX(SolgemaRichMenuControl):

    __allow_access_to_unprotected_subobjects__ = 1

    @memoize
    def showSolgemaRichMenuAction( self ):
        if not ISolgemaRichMenuMarker.providedBy(aq_inner(self.context)):
            return False
        return super(SolgemaRichMenuControlDX).showSolgemaRichMenuAction()
    
    showSolgemaRichMenuAction.__roles__ = None
