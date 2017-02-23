from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import CarouselPlugin


class CMSCarouselPlugin(CMSPluginBase):
    name = _("Carousel")
    module = _("Carousel")
    model = CarouselPlugin
    allow_children = True
    render_template = "cmsplugin_carousel/carousel.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super(CMSCarouselPlugin, self).render(context, instance, placeholder)
        context.update({
            'auto_id': 'carousel_%s' % instance.pk,
            'rotate_interval': instance.interval * 1000,
            'objects_list': instance.child_plugin_instances,
        })
        return context


class CaptionPlugin(CMSPluginBase):
    name = _('Carousel Caption')
    module = _("Carousel")
    allow_children = True
    render_template = 'cmsplugin_carousel/caption.html'


plugin_pool.register_plugin(CMSCarouselPlugin)
plugin_pool.register_plugin(CaptionPlugin)
