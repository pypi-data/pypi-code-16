from django.contrib import admin

from .models import Like


class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "target_content_type", "target_object_id", "timestamp"]
    list_select_related = True
    search_fields = ("user__username", )
    raw_id_fields = ("user", )


admin.site.register(Like, LikeAdmin)
