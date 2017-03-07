from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
import uuid


class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(_('Description'), max_length=255)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Area')
        verbose_name_plural = _('Areas')
        ordering = ('description',)

    def __str__(self):
        return self.description


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    area = models.ForeignKey(Area, verbose_name=_('Area'), related_name='cities')
    description = models.CharField(_('Description (uk)'), max_length=255)
    description_ru = models.CharField(_('Description (ru)'), max_length=255)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ('description',)

    def __str__(self):
        return self.description


class Office(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    description = models.CharField(_('Description (uk)'), max_length=255)
    description_ru = models.CharField(_('Description (ru)'), max_length=255)

    city = models.ForeignKey(City, verbose_name=_('City'), related_name='offices')

    number = models.PositiveIntegerField(_('Number'), default=1)
    sitekey = models.CharField(_('Site key'), max_length=10)

    international_shipping = models.BooleanField(_('International shipping'), default=False)
    place_max_weight_allowed = models.PositiveIntegerField(_('Max weight for place allowed'), default=0)
    total_max_weight_allowed = models.PositiveIntegerField(_('Total max weight allowed'), default=0)
    pos_terminal = models.BooleanField(_('POS terminal'), default=False)
    post_finance = models.BooleanField(_('Post finance'), default=False)
    bicycle_parking = models.BooleanField(_('Bicycle parking'), default=False)
    phone = models.CharField(_('Phone'), max_length=100, blank=True)

    delivery = JSONField(_('Delivery'), default=dict, blank=True)
    reception = JSONField(_('Reception'), default=dict, blank=True)

    latitude = models.DecimalField(_('Latitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('Longitude'), max_digits=9, decimal_places=6, null=True, blank=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Office')
        verbose_name_plural = _('Offices')
        ordering = ('number',)

    def __str__(self):
        return self.description
