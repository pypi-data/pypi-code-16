import pytest
from markio.marked import Meta


@pytest.fixture
def meta():
    return Meta(None, {'Foo': 'bar', 'Ham': 'spam'})


def test_meta_keys_are_case_insensitive(meta):
    assert meta['foo'] == 'bar'
    assert meta['Foo'] == 'bar'


def test_meta_defines_default_keys(meta):
    assert meta['author'] is None
    assert meta['Author'] is None
    assert meta['slug'] is None
    assert meta['Slug'] is None
    assert meta['tags'] == []
    assert meta['Tags'] == []


def test_can_add_tags(meta):
    meta.add_tag('ham')
    meta.add_tags('spam', 'eggs')
    assert meta.tags == ['ham', 'spam', 'eggs']