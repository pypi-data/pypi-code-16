from adminsortable.models import SortableMixin
from cms.models import CMSPlugin
from cms.models.fields import PageField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField


class CarouselPlugin(CMSPlugin):
    interval = models.PositiveIntegerField(_('Interval'), default=1)
    title = models.CharField(_('Title'), max_length=255, default='', blank=True)

    def __str__(self):
        return self.title or str(self.pk)

    def copy_relations(self, oldinstance):
        super(CarouselPlugin, self).copy_relations(oldinstance)
        for picture in oldinstance.pictures.all().iterator():
            picture.pk = None
            picture.plugin = self
            picture.save()


class CarouselPicture(SortableMixin):
    plugin = models.ForeignKey(CarouselPlugin, related_name='pictures')
    image = FilerImageField(verbose_name=_('Image'), related_name='+')
    alt_tag = models.CharField(_('Alt tag'), max_length=255, blank=True)
    text = models.TextField(verbose_name=_('Text over image'), blank=True)
    url = models.CharField(verbose_name=_('URL'), blank=True, null=True, max_length=500)
    page = PageField(verbose_name=_("Page"), blank=True, null=True)
    open_in_tab = models.BooleanField(verbose_name=_('Open in new window'))
    ordering = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ['ordering', ]

    def link(self):
        if self.page is not None:
            return self.page
        else:
            return self.url

    def __str__(self):
        return self.alt_tag
