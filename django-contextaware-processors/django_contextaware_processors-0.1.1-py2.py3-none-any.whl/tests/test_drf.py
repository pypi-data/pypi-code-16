# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest
from django.contrib.auth import get_user_model
try:
    from django.urls import resolve, reverse
except ImportError:
    from django.core.urlresolvers import resolve, reverse
from pytest_django.lazy_django import skip_if_no_django

from contextaware_processors.middleware import ContextawareProcessors


@pytest.fixture()
def api_rf():
    skip_if_no_django()
    try:
        from rest_framework.test import APIRequestFactory
    except ImportError:
        pytest.skip('Test skipped since djangorestframework is not present.')
    else:
        return APIRequestFactory()



@pytest.mark.django_db
def test_middleware_supports_djangorestframework_apiview(api_rf):
    user = get_user_model().objects.create_user('name', 'email@email.com', 'password')
    url = reverse('drf_user', kwargs={'pk': user.pk})
    view = resolve(url)
    request = api_rf.get(url)
    response = view.func(request, pk=user.pk)
    ContextawareProcessors().process_response(request, response)
    assert response.context_data is None
    assert 'args' in response.renderer_context
    assert 'kwargs' in response.renderer_context
    assert 'VIA_SETTINGS' in response.renderer_context
    assert 'VIA_SETTINGS2' in response.renderer_context
