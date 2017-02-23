# coding: utf-8
from __future__ import unicode_literals

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from .models import PageBreakPluginModel, PageBreakPagePluginModel
from .settings import PAGE_GET_PARAMETER


@plugin_pool.register_plugin
class PageBreakPlugin(CMSPluginBase):
    name = _('Page break')
    model = PageBreakPluginModel
    render_template = "cms/plugins/page-break.html"
    allow_children = True
    child_classes = ['PageBreakPagePlugin', ]

    def render(self, context, instance, placeholder):
        context = super(PageBreakPlugin, self). \
            render(context, instance, placeholder)
        plugins = instance.child_plugin_instances or []
        context['PAGE_GET_PARAMETER'] = PAGE_GET_PARAMETER
        context['page_number'] = \
            int(context['request'].GET.get(PAGE_GET_PARAMETER, 1))
        context['page_count'] = len(plugins)
        context['page_range'] = xrange(1, context['page_count'] + 1)
        context['page_list'] = plugins
        return context


@plugin_pool.register_plugin
class PageBreakPagePlugin(CMSPluginBase):
    name = _('Page break page')
    model = PageBreakPagePluginModel
    render_template = "cms/plugins/page-break-page.html"
    allow_children = True
    require_parent = True
    parent_classes = ['PageBreakPlugin']
