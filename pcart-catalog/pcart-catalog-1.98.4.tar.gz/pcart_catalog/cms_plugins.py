from django.utils.translation import ugettext as _
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import CollectionPluginModel


class CollectionPluginPublisher(CMSPluginBase):
    model = CollectionPluginModel  # model where plugin data are saved
    module = _("Catalog")
    name = _("Collection")  # name of the plugin in the interface
    render_template = "catalog/plugins/collection_plugin.html"

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context

plugin_pool.register_plugin(CollectionPluginPublisher)
