# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import django
import pytest
from django.conf import settings
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.files.base import ContentFile
from django.template import Context, Template as T


CTX = Context()

TEMPLATES = (
    ('{% load path2css %}{% css4path "/test/path/" %}', 'css/test-path.css'),
    ('{% load path2css %}{% css4path "/test/" prefix="HELLO" %}', 'css/HELLO-test.css'),
    ('{% load path2css %}{% css4path "/test/" prefix="HELLO_" %}', 'css/HELLO_test.css'),
    ('{% load path2css %}{% css4path "/test/" suffix="BYE" %}', 'css/test-BYE.css'),
    ('{% load path2css %}{% css4path "/test/" suffix="_BYE" %}', 'css/test_BYE.css'),
    # testing with different separators...
    ('{% load path2css %}{% css4path "test:path" midpoint="__" split_on=":" %}', 'css/test__path.css'),
)


@pytest.mark.parametrize("template_string,filename", TEMPLATES)
def test_templatetag(template_string, filename):
    storage = StaticFilesStorage(location=settings.STATICFILES_TEST_DIR)
    try:
        storage.save(name=filename, content=ContentFile("body { background: red; }"))
        resp = T(template_string).render(CTX).strip()
        expected_output = '<link href="{}{}" rel="stylesheet" type="text/css" />'.format(settings.STATIC_URL, filename)
        assert resp == expected_output
    finally:
        storage.delete(filename)

def test_templatetag_root_does_nothing():
    resp = T('{% load path2css %}{% css4path "//" %}').render(CTX).strip()
    assert resp == ''


def test_templatetag_multiple_parts_of_path():
    filenames = ('css/level1.css', 'css/level1-level2.css', 'css/level1-level2-level3.css')
    storage = StaticFilesStorage(location=settings.STATICFILES_TEST_DIR)
    try:
        for filename in filenames:
            storage.save(name=filename, content=ContentFile("body { background: red; }"))
        resp = T('{% load path2css %}{% css4path "/level1/level2/level3/" %}').render(CTX).strip()
        assert resp.split("\n") == [
            '<link href="{}css/level1.css" rel="stylesheet" type="text/css" />'.format(settings.STATIC_URL),
            '<link href="{}css/level1-level2.css" rel="stylesheet" type="text/css" />'.format(settings.STATIC_URL),
            '<link href="{}css/level1-level2-level3.css" rel="stylesheet" type="text/css" />'.format(settings.STATIC_URL)
        ]
    finally:
        for filename in filenames:
            storage.delete(filename)


@pytest.mark.xfail(condition=django.VERSION[0:2] < (1, 9),
                   reason="Django 1.8 doesn't have combination simple/assignment tags")
def test_templatetag_assignment():
    filename = 'css/test-path.css'
    storage = StaticFilesStorage(location=settings.STATICFILES_TEST_DIR)
    try:
        storage.save(name=filename, content=ContentFile("body { background: red; }"))
        resp = T('''{% load path2css %}{% css4path "/test/path/" as GOOSE %}
        before ... {% for part in GOOSE %}-{{part}}-{% endfor %} ... after
        ''').render(
            CTX,
        ).strip()
        parts = [x for x in resp.split() if x]
        assert parts == ['before', '...', '-{}css/test-path.css-'.format(settings.STATIC_URL), '...', 'after']
    finally:
        storage.delete(filename)
