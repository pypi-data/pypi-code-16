from django.contrib import admin
from .models import LogEntry, LogTag


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('message', 'level', 'logged_at', 'tags_display')
    readonly_fields = ('level', 'message', 'logged_at', 'tags_display')
    list_filter = ('level', )
    search_fields = ('message', 'tags__tag')

    def get_queryset(self, request):
        return super(LogEntryAdmin, self).get_queryset(
            request
        ).prefetch_related('tags')

    def tags_display(self, obj):
        return ', '.join(map(str, obj.tags.all()))
    tags_display.short_description = 'Tags'
