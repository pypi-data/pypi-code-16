# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from contextlib import contextmanager

import pytest
from django.utils.encoding import force_text

from contextaware_processors.response import ContextawareTemplateResponse, \
    AlreadyRendered


def _ctx_processor_1(request, context):
    return {'TEST': 1}


def _ctx_processor_2(request, context):
    if 'TEST' in context:
        return {'TEST2': 1, 'TEST': None}
    return {'NOTEST': False}


def _ctx_processor_3(request, context):
    return None

def _ctx_processor_4(request, context):
    return NotImplemented


@contextmanager
def render(response):
    old_context_data = response.context_data.copy()
    response.render()
    yield response
    response.context_data = old_context_data


@pytest.mark.parametrize("callbacks,context_data", (
    ([_ctx_processor_1], {'TEST': 1}),
    # TEST key gets replaced by second processor.
    ([_ctx_processor_1, _ctx_processor_2], {'TEST': None, 'TEST2': 1}),
    # TEST key wasn't in context when the _ctx_processor_2 ran, so its output is
    # different.
    ([_ctx_processor_2, _ctx_processor_1], {'NOTEST': False, 'TEST': 1}),
    # NotImplemented and None both mean do nothing.
    ([_ctx_processor_3, _ctx_processor_4], {}),
))
def test_contextaware_templateresponse(rf, callbacks, context_data):
    request = rf.get('/')
    response = ContextawareTemplateResponse(request=request, context={},
                                            template="admin/base.html")
    [response.add_context_callback(callback) for callback in callbacks]
    with render(response):
        assert response.context_data == context_data
    assert response.context_data == {}



def test_contextaware_templateresponse_error_if_rendered(rf):
    request = rf.get('/')
    response = ContextawareTemplateResponse(request=request, context={},
                                            template="admin/base.html")
    response.render()
    with pytest.raises(AlreadyRendered) as exc:
        response.add_context_callback(_ctx_processor_1)
    error_message = "Cannot apply a new context-mutating callback after " \
                    "rendering the content, without having to re-render it"
    assert error_message in force_text(exc.value)
