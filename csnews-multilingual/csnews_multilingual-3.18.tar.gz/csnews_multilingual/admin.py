from django.contrib import admin
from csnews_multilingual.models import Article, Tag, PhotoExtended
from csnews_multilingual.forms import PhotoAdminExtendedForm
from django.conf import settings
from tinymce.widgets import TinyMCE
from hvad.admin import TranslatableStackedInline
from hvad.admin import TranslatableAdmin
from photologue.admin import PhotoAdmin as PhotoAdminDefault
from photologue.models import Photo
from django.utils.translation import ugettext_lazy as _


def show_entry_thumbnail(item):
    if item.image:
        return item.image.admin_thumbnail()
    else:
        return None
    # return item.admin_thumbanail()
show_entry_thumbnail.short_description = 'Argazkia'
show_entry_thumbnail.allow_tags = True


class TagAdmin(TranslatableAdmin):
    def get_name(self, obj):
        return obj.safe_translation_getter('name')
    get_name.short_description = _('Name')

    list_display = ('get_name', 'added', 'all_translations')
    list_display_links = ('get_name',)
    ordering = ('-added',)
    search_fields = ['name', ]

    use_fieldsets = (
        (_("Language dependent"), {
            'fields': ('name',),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        return self.use_fieldsets


class ArticleAdmin(TranslatableAdmin):
    def get_title(self, obj):
        return obj.safe_translation_getter('title')
    get_title.short_description = _('Title')

    list_display = ('get_title', 'published', 'is_public', show_entry_thumbnail, 'all_translations')
    list_display_links = ('get_title',)
    ordering = ('-id',)
    search_fields = ['title', 'summary',]
    filter_horizontal = ('tags',)
    photologue_image_fields = ('image',)

    use_fieldsets = (
        (_("Language dependent"), {
            'fields': ('title', 'summary', 'body', 'tags'),
        }),
        (_("Common"), {
            'fields': ('published', 'image', 'is_public'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        return self.use_fieldsets

class TinyMCEArticleAdmin(ArticleAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('body', 'summary'):
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs=settings.TINYMCE_DEFAULT_CONFIG,
            ))
        return super(TinyMCEArticleAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class PhotoExtendedInline(TranslatableStackedInline):
    model = PhotoExtended
    can_delete = False


class PhotoAdmin(PhotoAdminDefault):
    form = PhotoAdminExtendedForm
    inlines = [PhotoExtendedInline, ]



admin.site.register(Article, TinyMCEArticleAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.unregister(Photo)
admin.site.register(Photo, PhotoAdmin)
