from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _

from haystack.forms import HighlightedModelSearchForm
from haystack.query import SearchQuerySet

from .paginator import DiggPaginator
from .settings import COMMON_PAGINATOR_PAGINATE_BY


class SearchPlugin(CMSPluginBase):
    cache = False
    model = CMSPlugin
    name = _("Search Form")
    render_template = "djangocms_search/search_results_plugin.html"
    search_queryset = SearchQuerySet

    def render(self, context, instance, placeholder):
        request = context.get('request')
        query = request.GET.get('q', None)
        page = request.GET.get('page', 1)
        form = HighlightedModelSearchForm(request.GET)
        form.search_queryset = SearchQuerySet
        if query:
            queryset = form.search()
            #TODO: filter pages and titles (for the unique page usage)
            # queryset = queryset.filter()
            # for item in queryset:
            #     print item.object
            if not request.user.is_authenticated():
                queryset = queryset.exclude(login_required=True)
            paginated = DiggPaginator(queryset, COMMON_PAGINATOR_PAGINATE_BY)
            context.update({
                'page_obj': paginated.page(page),
            })
        context.update({
            'instance': instance,
            'form': form,
        })
        return context


plugin_pool.register_plugin(SearchPlugin)
