# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Solgema.RichMenu.interfaces import IRichMenuSchema
from plone.app.registry.browser import controlpanel
from z3c.form.browser.checkbox import CheckBoxFieldWidget


class RichMenuControlPanelForm(controlpanel.RegistryEditForm):

    id = "RichMenuControlPanel"
    label = _(u"RichMenu Settings")
    description = _("""Lets you control how main menu tabs bar is constructed in your site. You can also control the behavior of each tab by going onto the tab itself and click on Navigation in the toolbar.""")
    schema = IRichMenuSchema
    schema_prefix = "plone"

    def updateFields(self):
        super(RichMenuControlPanelForm, self).updateFields()
        self.fields['sections_displayed_types'].widgetFactory = \
            CheckBoxFieldWidget
        self.fields['sections_wf_states_to_show'].widgetFactory = \
            CheckBoxFieldWidget


class RichMenuControlPanel(controlpanel.ControlPanelFormWrapper):
    form = RichMenuControlPanelForm
