from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^vote/(?P<question_id>[0-9]+)/$', views.vote, name='vote'),
]

