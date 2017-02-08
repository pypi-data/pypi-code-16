# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.calltoaction import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveCalltoactionLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ICollectiveCalltoactionSettings(Interface):

    show_always = schema.Bool(
        title=_(u'Show always, even when already seen'),
        description=_(
            u'description_always_show',
            default=(
                u'This is handy when you are experimenting or developing. '
                u'Otherwise you would need to clear your cookies '
                u'or mark the portlet as a new version '
                u'each time you change something.')),
        default=False,
    )

    show_global = schema.Bool(
        title=_(u'Show global action'),
        description=_(
            u'description_global_action',
            default=(
                u'This looks for a portlet in the navigation root, '
                u'which usually is the portal root. '
                u'It shows it on every page. '
                u'The timeout before showing the call to action, '
                u'is calculated from the first page visit. '
                u'The time spent on the site so far is stored on a cookie.')),
        default=False,
    )
