from pyml.helpers import render, safe
from pyml.helpers import attrs as _attrs


def tag(tag, data=None, attrs=None, request=None, kwargs=None, **attrs_kwargs):
    """
    Renders HTML tag.

    Args:
        tag:
            Tag name.
        data:
            Children elements for the given tag. Each element is rendered with
            the render_html() function.
        attrs:
            A dictionary of attributes.
        request:
            A request object that is passed to the render function when it is
            applied to children.
        **attr_kwargs:
            Keyword arguments are converted to additional attributes.

    Examples:
        >>> tag('a', 'Click me!', href='www.python.org')
        '<a href="www.python.org">Click me!</a>
    """

    if data is None:
        data = ''
    else:
        if kwargs:
            if 'request' in kwargs or request is None:
                data = render(data, **kwargs)
            else:
                data = render(data, request=request, **kwargs)
        else:
            data = render(data, request=request)
    attrs = _attrs(attrs, **attrs_kwargs)
    if attrs:
        attrs = safe(' ') + attrs
    return safe('<%s%s>%s</%s>' % (tag, attrs, data, tag))


def markdown(text, *, output_format='html5', **kwargs):
    """
    Renders Markdown content as HTML and return as a safe string.
    """

    from markdown import markdown

    return safe(markdown(text, output_format=output_format, **kwargs))


def sanitize(data, **kwargs):
    """
    Sanitize HTML and return as a safe string.
    """

    import bleach

    return safe(bleach.clean(data, **kwargs))
