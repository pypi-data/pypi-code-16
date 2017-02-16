from __future__ import absolute_import
from django.conf.urls import url
from rapidprototype import views

urlpatterns = [
    url(r'^placeholder/$',views.placeholder_image_view, name='placeholder'),
    url(r'^placeholder/(?P<width>\d+)x(?P<height>\d+)/$', views.placeholder_image_view, name='placeholder'),
    url(r'^placeholder/(?P<width>\d+)x(?P<height>\d+)/(?P<text>[\w\_\S\s]+)/$',
        views.placeholder_image_view,
        name='placeholder'
    ),
    url(r'^placeholder/(?P<text>[\w\_\S\s]+)/$',views.placeholder_image_view, name='placeholder'),
    url(r'^(?P<slug>[\w./-]*)/$', views.static_pages_view, name='page'),
    url(r'^$', views.static_pages_view, name='homepage'),
]
