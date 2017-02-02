from django.contrib.syndication.views import Feed
from csnews_multilingual.models import Article
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.utils.translation import ugettext as _


class LatestNews(Feed):
    title = _('News feed')
    link = "/%s/" % _('feed')
    description = _('News feed description')

    title_template = 'csnews_multilingual/rss_title.html'
    description_template = 'csnews_multilingual/rss_description.html'

    def items(self):
        return Article.objects.language(get_language()).filter(is_public=True).order_by('-published')[:20]

    def item_pubdate(self, item):
        return item.published

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]

    def item_link(self, item):
        return "%s?utm_source=rss_link&utm_medium=rss&utm_campaign=rss_feed" % reverse('csnews_article', args=[item.slug])
