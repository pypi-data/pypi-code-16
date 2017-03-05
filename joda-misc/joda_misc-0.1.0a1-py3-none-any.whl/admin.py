from django.contrib import admin, messages

from joda_core.documents.admin import DocumentsAdmin
from joda_misc.models import MiscDocument, MiscType


class MiscDocumentsAdmin(DocumentsAdmin):
    list_filter = ['misc_type', 'created_at', 'changed_at']
    search_fields = ['title', 'misc_type', 'notes', 'tags']


class MiscTypesAdmin(admin.ModelAdmin):
    ordering = ('name',)

    def has_delete_permission(self, request, obj=None):
        # If we're running the bulk delete action, estimate the number
        # of objects after we delete the selected items
        selected = request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)
        print(selected)
        if (selected and str(MiscType.DEFAULT_PK) in selected) \
                or (obj and obj.pk == MiscType.DEFAULT_PK):
            message = 'The first (default) type can not be deleted.'
            self.message_user(request, message, messages.INFO)
            return False

        return super(MiscTypesAdmin, self).has_delete_permission(request, obj)


admin.site.register(MiscDocument, MiscDocumentsAdmin)
admin.site.register(MiscType, MiscTypesAdmin)
