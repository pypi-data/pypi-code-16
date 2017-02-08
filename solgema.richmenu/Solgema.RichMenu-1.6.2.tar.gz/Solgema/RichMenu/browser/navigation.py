from Products.CMFPlone.utils import getFSVersionTuple
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.formlib import form
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Tuple
from zope.schema import Int

try:
    from plone.app.controlpanel.widgets import MultiCheckBoxThreeColumnWidget
    from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
    from plone.app.controlpanel.form import ControlPanelForm
    from Products.CMFDefault.formlib.schema import SchemaAdapterBase
except:
    pass
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Solgema.RichMenu.config import _
from Solgema.RichMenu.interfaces import IRichMenuSchema

if getFSVersionTuple()[0] == 4:

    class RichMenuNavigationControlPanelAdapter(SchemaAdapterBase):

        adapts(IPloneSiteRoot)
        implements(IRichMenuSchema)

        def __init__(self, context):
            super(RichMenuNavigationControlPanelAdapter, self).__init__(context)
            pprop = getToolByName(context, 'portal_properties')
            self.siteProps = pprop.site_properties
            self.navProps = pprop.navtree_properties
            self.ttool = getToolByName(context, 'portal_types')

        def get_sections_enable_submenues(self):
            return self.navProps.getProperty('sections_enable_submenues')

        def set_sections_enable_submenues(self, value):
            self.navProps._updateProperty('sections_enable_submenues', value)

        sections_enable_submenues = property(get_sections_enable_submenues, set_sections_enable_submenues)
        
        def get_enable_wf_state_filtering(self):
            return self.navProps.getProperty('enable_wf_state_filtering')

        def set_enable_wf_state_filtering(self, value):
            self.navProps._updateProperty('enable_wf_state_filtering', value)

        enable_wf_state_filtering = property(get_enable_wf_state_filtering, set_enable_wf_state_filtering)
        
        def get_submenu_display(self):
            return self.navProps.getProperty('submenu_display')

        def set_submenu_display(self, value):
            self.navProps._updateProperty('submenu_display', value)

        submenu_display = property(get_submenu_display, set_submenu_display)

        def get_sections_wf_states_to_show(self):
            return self.navProps.getProperty('sections_wf_states_to_show')

        def set_sections_wf_states_to_show(self, value):
            self.navProps._updateProperty('sections_wf_states_to_show', value)

        sections_wf_states_to_show = property(get_sections_wf_states_to_show, set_sections_wf_states_to_show)

        def get_sections_depth(self):
            return self.navProps.getProperty('sections_depth')

        def set_sections_depth(self, value):
            self.navProps._updateProperty('sections_depth', value)

        sections_depth = property(get_sections_depth, set_sections_depth)

        def get_sections_displayed_types(self):
            return self.navProps.getProperty('sections_displayed_types')

        def set_sections_displayed_types(self, value):
            self.navProps._updateProperty('sections_displayed_types', value)

        sections_displayed_types = property(get_sections_displayed_types, set_sections_displayed_types)
        
class RichMenuNavigationControlPanel(ControlPanelForm):
    label = _("RichMenu Settings")
    description = _("""Lets you control how main menu tabs bar is constructed in your site. You can also control the behavior of each tab by going onto the tab itself and click on Navigation in the toolbar.""")
    form_name = _("RichMenu Settings")
    form_fields = form.FormFields(IRichMenuSchema)
    form_fields['sections_displayed_types'].custom_widget = MultiCheckBoxThreeColumnWidget
    form_fields['sections_wf_states_to_show'].custom_widget = MultiCheckBoxVocabularyWidget
