
import flatpages.translation

from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from flatpages.forms import FlatpageForm
from flatpages.models import FlatPage


class FlatPageAdmin(TranslationAdmin):

    form = FlatpageForm

    list_display = ('url', 'title', )

    list_filter = ('registration_required', )

    search_fields = ('url', 'title', )


admin.site.register(FlatPage, FlatPageAdmin)
