# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.template import RequestContext as CTX, Template as T


def test_context_processor(rf):
    request = rf.get('/test/path/yeah/')
    resp = T('{{ PATH2CSS }}').render(CTX(request=request, dict_={})).strip()
    assert resp == 'test test-path test-path-yeah'
