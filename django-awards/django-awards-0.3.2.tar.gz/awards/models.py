# coding: utf-8
from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth import get_user_model
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class BadgeAward(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="badges_earned")
    slug = models.CharField(_('slug'), max_length=255)
    level = models.IntegerField(_('level'))

    points = models.PositiveIntegerField(_('points'), default=0)

    awarded_on = models.DateTimeField(_('awarded on'), default=datetime.now)
    created_on = models.DateTimeField(_('created on'), auto_now_add=True)

    class Meta:
        verbose_name = _('badge award')
        verbose_name_plural = _('badge awards')

    def __getattr__(self, attr):
        return getattr(self._badge, attr)

    def __str__(self):
        return self.name

    def __repr__(self):
        return u'<%s: %s (%s) awarded to %s>' % (
            self.__class__.__name__,
            self.name, self.level, self.user)

    def save(self, *args, **kwargs):
        super(BadgeAward, self).save(*args, **kwargs)
        self.get_user_points(self.user_id)

    @property
    def badge(self):
        return self

    @property
    def _badge(self):
        from .internals import badges
        return badges._registry[self.slug]

    @property
    def name(self):
        return unicode(self._badge.levels[self.level].name)

    @property
    def description(self):
        return unicode(self._badge.levels[self.level].description)

    @property
    def info(self):
        return self._badge.levels[self.level]

    @property
    def image_url(self):
        slug = getattr(self.info, 'slug', self.slug)
        return static(
            'icons/awards/{slug}.png'.format(slug=slug.replace('-', '_')))

    @property
    def progress(self):
        return self._badge.progress(self.user, self.level)

    @staticmethod
    def get_user_points(user_id):
        return BadgeAward.objects \
            .filter(user_id=user_id) \
            .aggregate(points=models.Sum('points')) \
            .get('points', 0)
