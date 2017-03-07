from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Area, City, Office


class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'changed')
    search_fields = ('id', 'description')


admin.site.register(Area, AreaAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'area', 'changed')
    search_fields = ('id', 'description', 'description_ru')
    raw_id_fields = ('area',)


admin.site.register(City, CityAdmin)


class OfficeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'description', 'city', 'changed',
        'international_shipping', 'pos_terminal', 'post_finance',
        'bicycle_parking',
        'total_max_weight_allowed', 'place_max_weight_allowed',
    )
    search_fields = ('id', 'description', 'description_ru', 'city__description')
    raw_id_fields = ('city',)

admin.site.register(Office, OfficeAdmin)
