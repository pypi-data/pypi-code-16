from collections import OrderedDict

import pytest
from mock import mock

from pyml.helpers import *
from pyml.helpers.attr import html_safe_natural_attr
from pyml.utils import singledispatch


def test_single_dispatch_example():
    @singledispatch
    def foo(x):
        return 42

    @foo.register(str)
    def _(x):
        return x

    @foo.register('collections.OrderedDict')
    def _(x):
        return dict(x)

    d = OrderedDict({3: 'three'})
    assert foo(1) == 42
    assert foo('two') == 'two'
    assert foo(d) == d


def test_attrs_examples():
    assert attrs([('foo', 42), ('bar', 'bar')]) == 'foo="42" bar="bar"'
    assert attrs(None, x=42) == 'x="42"'
    assert attrs({'foo': safe('bar')}) == 'foo="bar"'
    assert attrs({'foo': '<tag>'}) == 'foo="<tag>"'
    assert attrs({'foo': '"quote"'}) == 'foo="&quot;quote&quot;"'
    assert attrs({'foo': True, 'bar': False, 'baz': None}) == 'foo'


def test_attrs_protocol():
    class Foo:
        attrs = [('x', 1), ('y', 2)]

    assert attrs(Foo()) == 'x="1" y="2"'


def test_attrs_not_supported():
    with pytest.raises(TypeError):
        attr(b'sdfsdf')
    with pytest.raises(TypeError):
        attrs('sdfsdf')


def test_attr_examples():
    assert attr('foo') == 'foo'
    assert attr({'foo': 'bar'}) == '{&quot;foo&quot;: &quot;bar&quot;}'


def test_attr_names():
    assert html_safe_natural_attr('data-foo') == 'data-foo'
    assert html_safe_natural_attr('data_foo') == 'data-foo'
    assert html_safe_natural_attr('v-bind:foo') == 'v-bind:foo'
    assert html_safe_natural_attr(':foo') == ':foo'
    assert html_safe_natural_attr('@foo') == '@foo'

    invalid = ['foo bar', 'foo"', 'foo=', 'foo\'']
    for name in invalid:
        with pytest.raises(ValueError):
            html_safe_natural_attr(name)


def test_tag_examples():
    assert tag('div', 'foo', class_='c') == '<div class="c">foo</div>'
    assert tag('script', src='foo.js') == '<script src="foo.js"></script>'
    assert tag('a', ['a', 'b'], kwargs={'foo': True}) == '<a>a\nb</a>'


def test_markdown():
    assert markdown('#foo\n') == '<h1>foo</h1>'


def test_sanitize():
    assert sanitize('<b>foo</b>') == '<b>foo</b>'
    assert sanitize('<script>') == '&lt;script&gt;'


def test_hyperlink_examples():
    link = '<a href="bar">foo</a>'
    assert hyperlink('foo') == '<a>foo</a>'
    assert hyperlink('foo', 'bar') == link
    assert hyperlink({'href': 'bar', 'content': 'foo'}) == link
    assert hyperlink('foo', attrs={'href': 'bar'}) == link
    assert hyperlink({'content': 'foo'}, attrs={'href': 'bar'}) == link


def test_hyperlink_not_supported():
    with pytest.raises(TypeError):
        hyperlink(b'sdfsdf')


def test_render_examples():
    assert render('bar') == 'bar'
    assert render(['foo', 'bar']) == 'foo\nbar'


def test_render_not_supported():
    with pytest.raises(TypeError):
        render(b'sdfsdf')


def test_register_template():
    class Foo:
        pass

    render.register_template(Foo)
    result = []

    def f(*args, **kwargs):
        result.append((args, kwargs))
        return ''

    with mock.patch('pyml.helpers.render._render_template', f):
        foo = Foo()
        x = render(foo)
        args, kwargs = result.pop()
        assert args == (['pyml/foo.html', 'pyml/foo.jinja2'],)
        assert sorted(kwargs) == ['context', 'request']
        request = kwargs['context']['request']
        assert hasattr(request, 'POST')
        assert kwargs['context'] == {'foo': foo, 'request': request}


def test_register_template_using_decorator():
    class Foo:
        pass

    @render.register_template(Foo)
    def get_context(x, request, **kwargs):
        return {'x': x, 'request': None}

    result = []

    def f(*args, **kwargs):
        result.append((args, kwargs))
        return ''

    with mock.patch('pyml.helpers.render._render_template', f):
        foo = Foo()
        x = render(foo)
        args, kwargs = result.pop()
        assert kwargs['context'] == {'x': foo, 'request': None}
