from django.conf.urls import url
from csnews_multilingual.feeds import LatestNews
from django.utils.translation import ugettext_lazy as _
# feed_dict = {'rss': LatestNews}

from csnews_multilingual import views

urlpatterns = [
    url(r'^$', views.index, name='csnews_index'),
    url(_(r'^tag/(?P<tag_slug>[\-\d\w]+)$'), views.tag_index, name='csnews_tag'),
    url(_(r'^feed$'), LatestNews(), name='csnews_feed'),
    url(_(r'^archive$'), views.archive, name='csnews_archive'),
    url(_(r'^(?P<article_slug>[\-\d\w]+)$'), views.article_index, name='csnews_article'),
]
