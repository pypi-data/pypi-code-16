# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.http import Http404
from django.http import HttpResponse
from django.views.generic import TemplateView

from .apps_settings import ACME_CHALLENGE_URL_SLUG, ACME_CHALLENGE_TEMPLATE_CONTENT


class ACMEChallengeView(TemplateView):
    def get(self, request, *args, **kwargs):
        if ACME_CHALLENGE_URL_SLUG and ACME_CHALLENGE_TEMPLATE_CONTENT:
            if self.kwargs['challenge_slug'] == ACME_CHALLENGE_URL_SLUG:
                return HttpResponse(ACME_CHALLENGE_TEMPLATE_CONTENT)
        raise Http404("Invalid ACME challenge config")
