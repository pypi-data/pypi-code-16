import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pcart_catalog.models import (
    Collection,
    ProductType,
    Product,
    ProductVariant,
    ProductImage,
)


class XMLFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(_('File name'), max_length=255)
    added = models.DateTimeField(_('Added'), auto_now_add=True)

    class Meta:
        verbose_name = _('XML import file')
        verbose_name_plural = _('XML import files')

    def __str__(self):
        return self.filename

    def run_import_task(self):
        from .tasks import import_goods
        # Execute import tasks in 30 seconds from now
        return import_goods.apply_async(args=[self.pk], countdown=30)


class ProductImportLogMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, verbose_name=_('Product'), related_name='import_log_messages')
    variant = models.ForeignKey(
        ProductVariant, verbose_name=_('Product variant'),
        related_name='import_log_messages', null=True, blank=True)

    file = models.ForeignKey(
        XMLFile, verbose_name=_('XML import file'),
        related_name='import_log_messages')
    message = models.TextField(_('Message'), blank=True, default='')
    added = models.DateTimeField(_('Added'), auto_now_add=True)

    class Meta:
        verbose_name = _('Product import log message')
        verbose_name_plural = _('Product import log messages')

    def __str__(self):
        return self.message


class ProductTypeRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=255)
    alternate_uuid = models.UUIDField(
        _('UUID in 1C'),
        unique=True,
        help_text=_('UUID of the product category in 1C system.'))
    product_type = models.OneToOneField(
        ProductType,
        verbose_name=_('Product type'),
        related_name='product_type_relation')
    collection = models.OneToOneField(
        Collection,
        verbose_name=_('Collection'), related_name='product_type_relation',
        help_text=_('Add the products of specified type to a collection.'),
    )

    class Meta:
        verbose_name = _('Product type relation')
        verbose_name_plural = _('Product type relations')

    def __str__(self):
        return self.title


class ExtraCollectionRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag_name = models.CharField(_("Tag name"), max_length=70)
    collection = models.OneToOneField(
        Collection,
        verbose_name=_('Collection'),
        related_name='extra_collection_relation',
        help_text=_('Link MetaContent/* tag with a collection.'),
    )

    class Meta:
        verbose_name = _('Extra collection relation')
        verbose_name_plural = _('Extra collections relations')

    def __str__(self):
        return self.tag_name
