# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.template.response import TemplateResponse

from contextaware_processors.middleware import ContextawareProcessors
from contextaware_processors.response import ContextawareTemplateResponse


def via_settings_1(request, context):
    return {'VIA_SETTINGS': 1}


def via_settings_2(request, context):
    if 'VIA_SETTINGS' in context and context['VIA_SETTINGS'] == 1:
        return {'VIA_SETTINGS': 'Yay', 'VIA_SETTINGS2': 1}
    return {'VIA_SETTINGS': False}


def via_contextaware_templateresponse(request, context):
    return {'CONTEXTAWARE': 1}



def test_middleware_applying_to_templateresponse(rf):
    request = rf.get('/')
    response = TemplateResponse(request=request, context={},
                                template="admin/base.html")
    ContextawareProcessors().process_response(request, response)
    assert response.context_data == {'VIA_SETTINGS': 'Yay', 'VIA_SETTINGS2': 1}


def test_middleware_applying_to_contextawaretemplateresponse(rf):
    request = rf.get('/')
    response = ContextawareTemplateResponse(request=request, context={},
                                            template="admin/base.html")
    response.add_context_callback(via_contextaware_templateresponse)
    ContextawareProcessors().process_response(request, response)
    # Have to render to ensure everything is applied
    response.render()
    assert response.context_data == {'CONTEXTAWARE': 1,
                                     'VIA_SETTINGS': 'Yay',
                                     'VIA_SETTINGS2': 1}


def test_middleware_doesnt_apply_if_already_rendered(rf):
    request = rf.get('/')
    response = TemplateResponse(request=request, context={},
                                template="admin/base.html")
    response.render()
    ContextawareProcessors().process_response(request, response)
    assert response.context_data == {}
