import pytest

from sulfur.conversions import js_to_python, python_to_js, js_source


def test_basic_conversions_of_common_types():
    for x in [1, 1.0, 'foo', True, None, [1, 2], {"answer": 42}]:
        assert js_to_python(x) == x
        assert python_to_js(x) == x

    for x in [1, 1.0, 'foo', [1, 2], {"answer": 42}]:
        assert repr(x) == js_source(x)

    assert js_source(True) == 'true'
    assert js_source(None) == 'null'


def test_basic_conversion_error():
    with pytest.raises(TypeError):
        js_source(1+2j)