# -*- coding: utf-8 -*-
from collective.calltoaction.interfaces import ICollectiveCalltoactionSettings
from collective.calltoaction.portlets.calltoactionportlet import ICallToActionPortlet  # noqa
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletRetriever
from plone.registry.interfaces import IRegistry
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility


class CallToActionViewlet(ViewletBase):

    def update(self):
        self.data = []
        # For Plone 5 this can be nice:
        # footer = getUtility(IPortletManager, name='plone.footerportlets')
        # But portlets in Plone 5 need to be based on z3c.form, so it may be
        # tricky to support Plone 4 and 5 with the same code base.
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ICollectiveCalltoactionSettings, check=False)
        self.show_global = settings.show_global
        if self.show_global:
            target = api.portal.get_navigation_root(self.context)
        else:
            target = self.context
        self.show_always = settings.show_always
        for name in ('plone.leftcolumn', 'plone.rightcolumn'):
            manager = getUtility(IPortletManager, name=name)
            retriever = getMultiAdapter(
                (target, manager), IPortletRetriever)
            portlets = retriever.getPortlets()
            for portlet in portlets:
                assignment = portlet['assignment']
                if not ICallToActionPortlet.providedBy(assignment):
                    continue
                renderer = self._data_to_portlet(manager, assignment.data)
                # Pass the original context to the renderer so we can see
                # if this is the same as the referenced form, if set.
                html = renderer.render(orig_context=self.context)
                if not html:
                    # Happens for example when the portlet references a form,
                    # and the context is this same form.
                    continue
                info = {
                    'assignment': assignment,
                    'css_class': self.css_manager_name(name),
                    'html': html,
                }
                self.data.append(info)

    def css_manager_name(self, name):
        if name == 'plone.leftcolumn':
            return 'manager_left'
        if name == 'plone.rightcolumn':
            return 'manager_right'
        return name

    def _data_to_portlet(self, manager, data):
        """Helper method to get the correct IPortletRenderer for the given
        data object.

        Adapted from plone.portlets/manager.py _dataToPortlet.
        """
        if self.show_global:
            target = api.portal.get_navigation_root(self.context)
            # Use dummy view for the target context.
            view = BrowserView(target, self.request)
        else:
            target = self.context
            view = self.view
        return getMultiAdapter((target, self.request, view,
                                manager, data, ), IPortletRenderer)
