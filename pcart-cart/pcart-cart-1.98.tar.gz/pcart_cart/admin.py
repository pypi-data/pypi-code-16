from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Cart, OrderNumberFormat, Order


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'site', 'added', 'changed')
    raw_id_fields = ('customer',)
    search_fields = ['id', 'customer']
    date_hierarchy = 'changed'

admin.site.register(Cart, CartAdmin)


class OrderNumberFormatAdmin(admin.ModelAdmin):
    list_display = ('site', 'template', 'last_number', 'example')

    def example(self, obj):
        return obj.template % obj.last_number
    example.short_description = _('Example')

admin.site.register(OrderNumberFormat, OrderNumberFormatAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'site', 'id', 'added', 'changed')
    search_fields = ('id', 'customer', 'number')
    date_hierarchy = 'added'
    raw_id_fields = ('customer',)
    readonly_fields = ('number',)
    ordering = ('-added',)

admin.site.register(Order, OrderAdmin)
