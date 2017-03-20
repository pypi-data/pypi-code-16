from django.contrib import admin
# from django.conf import settings
from .models import (
    XMLFile,
    ProductImportLogMessage,
    ProductTypeRelation,
    ExtraCollectionRelation,
)
# from django.utils.translation import ugettext as _


class XMLFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'added')
    search_fields = ('filename',)
    date_hierarchy = 'added'


admin.site.register(XMLFile, XMLFileAdmin)


class ProductImportLogMessageAdmin(admin.ModelAdmin):
    list_display = ('product', 'variant', 'file', 'message', 'added')
    raw_id_fields = ('product', 'variant', 'file')
    date_hierarchy = 'added'


admin.site.register(ProductImportLogMessage, ProductImportLogMessageAdmin)


class ProductTypeRelationAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'alternate_uuid',
        'product_type', 'collection')

admin.site.register(ProductTypeRelation, ProductTypeRelationAdmin)


class ExtraCollectionRelationAdmin(admin.ModelAdmin):
    list_display = ('tag_name', 'collection')

admin.site.register(ExtraCollectionRelation, ExtraCollectionRelationAdmin)
