import logging
from Acquisition import aq_inner, aq_parent, aq_base
from persistent import Persistent
from Products.Five import BrowserView
from Products.Five.utilities import marker as fivemarker
from Products.CMFCore.utils import getToolByName
from zope import component, schema, interface
from zope.annotation import factory
from zope.lifecycleevent import ObjectModifiedEvent
from z3c.form import form, field, button, subform
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE
from plone.z3cform.layout import wrap_form
from Products.CMFPlone.utils import getFSVersionTuple
try:
    from plone.supermodel import model
    has_p5 = getFSVersionTuple()[0] == 5
except:
    has_p5 = False
try:
    from z3c.relationfield.schema import RelationChoice, RelationList
    from plone.app.vocabularies.catalog import CatalogSource
    from plone.app.z3cform.widget import RelatedItemsFieldWidget
    has_rel = True
except:
    has_rel = False
try:
    from plone.formwidget.contenttree import ContentTreeFieldWidget, UUIDSourceBinder
    has_ctree = True
except:
    has_ctree = False
from zope.interface import implements, directlyProvidedBy
from Products.CMFDynamicViewFTI.interface import IBrowserDefault
from zope.component import getMultiAdapter
from plone.memoize.view import memoize
from plone.memoize.ram import global_cache
from plone.app.layout.navigation.defaultpage import isDefaultPage
from Solgema.RichMenu.interfaces import ISolgemaRichMenuAttributes, ISolgemaRichMenuMarker
from Solgema.RichMenu.config import _
LOG = logging.getLogger('Solgema.RichMenu')

class SolgemaRichMenuAttributesAdapter(Persistent):

    implements(ISolgemaRichMenuAttributes)
    component.adapts(interface.Interface)
    def __init__(self):
        for iface in list(directlyProvidedBy(self)):
            for field in [iface.get(name) for name in iface.names() if schema.interfaces.IField.providedBy(iface.get(name))]:
                setattr(self, field.__name__, field.default)

SolgemaRichMenuAttributes = factory(SolgemaRichMenuAttributesAdapter)

class z3cManageSolgemaRichMenuAttributes(form.EditForm):
    
    label = _('Rich Menu parameters')

    @property
    def fields(self):
        fields = field.Fields(ISolgemaRichMenuAttributes)
        portal_quickinstaller = getToolByName(self.context, 'portal_quickinstaller')
        if has_rel:
            fields['section_menu_item'].widgetFactory[INPUT_MODE] = RelatedItemsFieldWidget
        elif not has_rel and has_ctree:
            fields['section_menu_item'].widgetFactory[INPUT_MODE] = ContentTreeFieldWidget
        return fields
    
    def applyChanges(self, data):
        fivemarker.mark(self.context, ISolgemaRichMenuMarker)
        changes = super(z3cManageSolgemaRichMenuAttributes, self).applyChanges(data)
        aq_inner(self.context).reindexObject()
#        global_cache.invalidate('Solgema.RichMenu.viewlets.common.firstLevelTabs')
        return changes

ManageSolgemaRichMenuAttributes = wrap_form(z3cManageSolgemaRichMenuAttributes)

class SolgemaRichMenuControl(BrowserView):

    __allow_access_to_unprotected_subobjects__ = 1

    @memoize
    def showSolgemaRichMenuAction( self ):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = getattr(portal_properties, 'site_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        sublevels = getattr(navtree_properties, 'sections_depth', 1)
        
        object_url = context_state.canonical_object_url()
        navigation_root_url = portal_state.navigation_root_url()
        sub_url = object_url.replace(navigation_root_url, '')
        if sub_url.count('/') > sublevels:
            return False
        
        if context_state.is_default_page():
            return False
        if site_properties.getProperty('disable_nonfolderish_sections', False) and not context_state.is_structural_folder():
            return False
        if hasattr(self.context, 'exclude_from_nav'):
            if callable(self.context.exclude_from_nav):
                return not self.context.exclude_from_nav()
            else:
                return not self.context.exclude_from_nav
        if getattr(self.context, 'excludeFromGlobalnav', False):
            return False

        portal_type = getattr(aq_base(self.context), 'portal_type', None)
        if portal_type:
            if navtree_properties.getProperty('sections_displayed_types', False):
                portal_types = navtree_properties.getProperty('sections_displayed_types')
            else:
                portal_types = ['Folder', 'Collection', 'Topic', 'Collage', 'FormFolder']
            if not portal_type in portal_types:
                return False
        
        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            workflow_state = context_state.workflow_state()
            if hasattr(navtree_properties, 'sections_wf_states_to_show'):
                workflow_states = navtree_properties.getProperty('sections_wf_states_to_show', ())
            else:
                workflow_states = navtree_properties.getProperty('wf_states_to_show', ())
            if not workflow_state in workflow_states:
                return False
            
        return True

    showSolgemaRichMenuAction.__roles__ = None
        
