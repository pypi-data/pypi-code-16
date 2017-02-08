# -*- coding: utf-8 -*-
from collective.calltoaction import _
from collective.calltoaction.interfaces import ICollectiveCalltoactionSettings
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from z3c.form import form


class CalltoactionControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = ICollectiveCalltoactionSettings

CalltoactionControlPanelView = layout.wrap_form(
    CalltoactionControlPanelForm, ControlPanelFormWrapper)
CalltoactionControlPanelView.label = _(u'Call to action settings')
