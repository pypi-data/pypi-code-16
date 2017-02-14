# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url

from .views import ACMEChallengeView


urlpatterns = [
    url(
        r'^.well-known/acme-challenge/(?P<challenge_slug>[\w\-]+)/?$',
        ACMEChallengeView.as_view(),
        name='acme-challenge'
    ),
]
