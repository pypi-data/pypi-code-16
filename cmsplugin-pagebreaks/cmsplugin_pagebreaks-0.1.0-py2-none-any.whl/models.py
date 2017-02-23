# coding: utf-8
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from cms.models.pluginmodel import CMSPlugin


class PageBreakPluginModel(CMSPlugin):

    def __unicode__(self):
        plugins = self.child_plugin_instances or []
        return _(u"%s pages") % len(plugins)


class PageBreakPagePluginModel(CMSPlugin):

    def __unicode__(self):
        return _("page %d") % self.get_position_in_placeholder()
