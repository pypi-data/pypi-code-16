from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CarouselPlugin(CMSPlugin):
    interval = models.PositiveIntegerField(_('Interval'), default=5)
    title = models.CharField(_('Title'), max_length=255, default='', blank=True)

    def __str__(self):
        return self.title or str(self.pk)
