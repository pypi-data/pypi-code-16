from django.contrib import admin
from .models import SiteSetting, SidebarLink, TitlebarLink

class SidebarLinkInline(admin.TabularInline):
    model = SidebarLink

class TitlebarLinkInline(admin.TabularInline):
    model = TitlebarLink


class SiteSettingAdmin(admin.ModelAdmin):
    inlines = [
        SidebarLinkInline,
        TitlebarLinkInline,
    ]
    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else True
    def has_delete_permission(self, request, obj=None):
        return False if self.model.objects.count() <= 1 else True
    def get_actions(self, request):
        actions = super(SiteSettingAdmin, self).get_actions(request)
        if self.model.objects.count() <= 1:
            del actions['delete_selected']
        return actions

admin.site.register(SiteSetting, SiteSettingAdmin)
