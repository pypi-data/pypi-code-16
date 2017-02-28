from daterange_filter.filter import DateRangeFilter
from django.http import HttpResponse
from import_export import resources
from molo.yourwords.admin import YourWordsCompetitionAdmin
from molo.yourwords.models import YourWordsCompetitionEntry, \
    YourWordsCompetition
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
    ModelAdminGroup,
)
from wagtail.contrib.modeladmin.views import IndexView


class DateFilter(DateRangeFilter):
    template = 'admin/yourwords/yourwords_date_range_filter.html'


class YourWordsEntriesResource(resources.ModelResource):
    class Meta:
        model = YourWordsCompetitionEntry
        exclude = ('id', '_convert', 'article_page')


class ModelAdminTemplate(IndexView):
    def post(self, request, *args, **kwargs):

        drf__submission_date__gte = request.GET.get(
            'drf__submission_date__gte'
        )
        drf__submission_date__lte = request.GET.get(
            'drf__submission_date__lte'
        )
        is_read__exact = request.GET.get('is_read__exact')
        is_shortlisted__exact = request.GET.get('is_shortlisted__exact')
        is_winner__exact = request.GET.get('is_winner__exact')

        filter_list = {
            'submission_date__range': (drf__submission_date__gte,
                                       drf__submission_date__lte)
            if drf__submission_date__gte and
            drf__submission_date__lte else None,
            'is_read': is_read__exact,
            'is_shortlisted': is_shortlisted__exact,
            'is_winner': is_winner__exact
        }

        arguments = {}

        for key, value in filter_list.items():
            if value:
                arguments[key] = value

        dataset = YourWordsEntriesResource().export(
            YourWordsCompetitionEntry.objects.filter(**arguments))

        response = HttpResponse(dataset.csv, content_type="csv")
        response['Content-Disposition'] = \
            'attachment; filename=yourwords_entries.csv'
        return response

    def get_template_names(self):
        return 'admin/yourwords/model_admin_template.html'


class YourWordsEntriesModelAdmin(ModelAdmin):
    model = YourWordsCompetitionEntry
    menu_label = 'Entries'
    menu_icon = 'edit'
    index_view_class = ModelAdminTemplate
    add_to_settings_menu = False
    list_display = ['story_name', 'user', 'hide_real_name',
                    'submission_date', 'is_read', 'is_shortlisted',
                    'is_winner', '_convert']

    list_filter = [('submission_date', DateFilter), 'is_read',
                   'is_shortlisted', 'is_winner', 'competition__slug']

    search_fields = ('story_name',)

    def _convert(self, obj, *args, **kwargs):
        if obj.article_page:
            return (
                '<a href="/admin/pages/%d/edit/">Article Page</a>' %
                obj.article_page.id)
        return (
            '<a href="/django-admin/yourwords/yourwordscompetitionentry'
            '/%d/convert/" class="addlink">Convert to article</a>' %
            obj.id)

    _convert.allow_tags = True
    _convert.short_description = ''


class ModelAdminCompetitionTemplate(IndexView):
    def get_template_names(self):
        return 'admin/yourwords/model_admin_competition_template.html'


class YourWordsModelAdmin(ModelAdmin, YourWordsCompetitionAdmin):
    model = YourWordsCompetition
    menu_label = 'Competitions'
    menu_icon = 'doc-full'
    index_view_class = ModelAdminCompetitionTemplate
    add_to_settings_menu = False
    list_display = ['entries', 'start_date', 'end_date', 'status',
                    'number_of_entries']

    search_fields = ('story_name',)

    def entries(self, obj, *args, **kwargs):
        url = '/admin/yourwords/yourwordscompetitionentry/'
        return '<a href="%s?competition__slug=%s">%s</a>' % (
            url, obj.slug, obj)

    entries.allow_tags = True
    entries.short_description = 'Title'


class YourWordsAdminGroup(ModelAdminGroup):
    menu_label = 'YourWords'
    menu_icon = 'folder-open-inverse'
    menu_order = 400
    items = (YourWordsEntriesModelAdmin, YourWordsModelAdmin)


modeladmin_register(YourWordsAdminGroup)
