from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse, NoReverseMatch
from pcart_catalog.models import Product, ProductVariant
from pcart_customers.models import Customer
import uuid


class Review(MPTTModel):
    STATUS_CHOICES = (
        ('unpublished', _('Unpublished')),
        ('published', _('Published')),
        ('flagged', _('Flagged')),
        ('spam', _('Spam')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(
        Site, verbose_name=_('Site'), related_name='reviews', on_delete=models.PROTECT)
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', db_index=True,
        verbose_name=_('Parent'),
    )

    customer = models.ForeignKey(
        Customer, verbose_name=_('Customer'), related_name='reviews', null=True, blank=True)

    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'))

    type = models.CharField(_('Type'), default='review', max_length=30)

    product = models.ForeignKey(Product, verbose_name=_('Product'), related_name='reviews')
    product_variant = models.ForeignKey(
        ProductVariant, verbose_name=_('Product variant'), null=True, blank=True,
        related_name='reviews',
    )

    pros = models.CharField(_('Pros'), blank=True, default='', max_length=255)
    cons = models.CharField(_('Cons'), blank=True, default='', max_length=255)
    comment = models.TextField(_('Comment'), blank=True, default='')

    rating = models.FloatField(_('Rating'), default=0)
    extra_ratings = ArrayField(
        models.FloatField(),
        verbose_name=_('Extra ratings'),
        blank=True,
        default=list,)
    extra_data = JSONField(_('Extra data'), default=dict, blank=True)

    status = models.CharField(_('Status'), default='unpublished', max_length=30, choices=STATUS_CHOICES)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '%s#review%s' % (self.product.get_absolute_url(), self.id)
