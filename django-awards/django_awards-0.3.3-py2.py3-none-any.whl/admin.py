from django.contrib import admin

from .models import BadgeAward


@admin.register(BadgeAward)
class BadgeAwardAdmin(admin.ModelAdmin):
    THUMB_SIZE = 40

    list_display = ('user', 'slug', 'name', 'level', 'points', 'awarded_on')
    raw_id_fields = ('user', )
    list_filter = ('slug', 'level', 'points', )
    search_fields = ('slug', 'level')
