import pytest
from sulfur.queriable import *


@pytest.fixture(params=['#foo', '#foo-bar', '#foo_bar', '#FooBar'])
def id(request):
    return request.param


@pytest.fixture(params=['foo', 'FOO', 'Foo', 'foo-bar'])
def tag(request):
    return request.param


@pytest.fixture(params=['.foo', '.FOO', '.Foo', '.foo-bar'])
def cls(request):
    return request.param


@pytest.fixture
def queryable():
    return QueriableMixin()


def test_correctly_identify_id_selectors(id, tag, cls):
    assert is_id_selector(id)
    assert not is_id_selector(tag)
    assert not is_id_selector(cls)


def test_correctly_identify_class_selectors(id, tag, cls):
    assert is_class_selector(cls)
    assert not is_class_selector(tag)
    assert not is_class_selector(id)


def test_correctly_identify_tag_selectors(id, tag, cls):
    assert is_tag_selector(tag)
    assert not is_tag_selector(cls)
    assert not is_tag_selector(id)


def test_finds_correct_query_type(queryable, id, tag, cls):
    assert queryable._get_query_method_suffix(id) == 'id'
    assert queryable._get_query_method_suffix(tag) == 'tag_name'
    assert queryable._get_query_method_suffix(cls) == 'class_name'
    assert queryable._get_query_method_suffix('[type=submit]') == 'css_selector'
