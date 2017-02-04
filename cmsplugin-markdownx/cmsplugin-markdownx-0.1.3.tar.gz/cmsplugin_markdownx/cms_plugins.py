from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from cmsplugin_markdownx.models import MarkdownxPlugin
from cmsplugin_markdownx.forms import MarkdownxPluginForm

class MarkdownxCMSPlugin(CMSPluginBase):
    model = MarkdownxPlugin
    form = MarkdownxPluginForm
    name = _('Markdown')
    render_template = 'cmsplugin_markdownx/markdownx.html'
    change_form_template = 'cmsplugin_markdownx/change_form.html'
    # i wonder what this does? text_enabled = True
    cache = False

    def render(self, context, instance, placeholder):
        context = super(MarkdownxCMSPlugin, self).render(context, instance, placeholder)
        return context

#todo: parameterize these hard-coded media files.
    class Media:
        css = {
            "all": (getattr(settings, "CMSPLUGIN_MARKDOWNX_CODEHILITE_CSS"), "markdownx/admin/css/markdownx.css")
        }
        js = ("markdownx/js/markdownx.js",)


plugin_pool.register_plugin(MarkdownxCMSPlugin)
