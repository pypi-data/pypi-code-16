import pytest

from sulfur import ValidationError
from sulfur.simplehtml5 import validate


@pytest.fixture(
    params=[
        '<!DOCTYPE bad>...',
        '<!DOCTYPE bad<html></html>',
        '<foo></bar>',
        '<foo><bar></foo>',
        '<foo><bar></foo></bar>',
        '<!-- comment that does not end'
        '<foo *bad-attr*="foo">',
        '<foo attr=*bad-value*>',
        '</closing>',
    ]
)
def bad(request):
    return request.param


@pytest.fixture(
    params=[
        '<!DOCTYPE html><html><body>foo</body></html>'
    ]
)
def ok(request):
    return request.param


def assert_ok(data, html_identity=True):
    ast = validate(data)
    if html_identity:
        html_render = ast.render().strip()
        data = data.strip()
        assert html_render == data


def test_validate_simple_doctype_document():
    assert_ok("<!DOCTYPE html>")


def test_validate_simple_document():
    assert_ok("<!DOCTYPE html><head></head><body></body>")


def test_validate_tag_with_attribute():
    assert_ok('<div id="foo"></div>')


def test_validate_tag_with_unquoted_attribute():
    assert_ok('<div id=foo></div>')


def test_validate_tag_with_boolean_attribute():
    assert_ok('<div is-a-tag></div>')


def test_validate_self_closing_tag():
    assert_ok('<p>foo<br></p>')
    assert_ok('<p>foo<br/></p>', False)


def test_validate_bytestring():
    assert_ok(b'<div id="foo"></div>', False)


def test_comment():
    assert_ok('<!-- comment --><p>foo</p>')


def test_invalid_examples(bad):
    with pytest.raises(ValidationError):
        validate(bad)


def test_ok(ok):
    assert_ok(ok)
