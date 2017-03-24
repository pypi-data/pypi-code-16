from contextlib import contextmanager

from lazyutils import lazy
from selenium.common.exceptions import ElementNotSelectableException
from selenium.webdriver.remote.webelement import WebElement

from .conversions import js_to_python, python_to_js
from .errors import DoesNotAcceptInputError
from .queriable import QueriableMixin
from .queryset import QuerySet
from .utils import Position, Shape, random_id

FILL_TAGS_WHITELIST = ['input', 'textarea', 'form']


class Element(QueriableMixin):
    """
    HTML element of a web page.
    """

    @property
    def id(self):
        """
        HTML id for element.
        """
        return self.attr('id') or None

    @id.setter
    def id(self, value):
        script = (
            'arguments[0].id = arguments[1]'
        )
        self._driver.selenium.execute_script(script, self._element, str(value))

    @property
    def selenium_id(self):
        """
        A unique id for element.
        """
        return self._element.id

    @property
    def selenium(self):
        """
        Direct access to selenium API.
        """
        return self._element

    Se = selenium

    @property
    def is_visible(self):
        """
        True if element is visible on screen.
        """
        return self._element.is_displayed()

    @property
    def is_enabled(self):
        """
        True if element is enabled.
        """
        return self._element.is_enabled()

    @property
    def is_selected(self):
        """
        True is element has focus. Some elements cannot have focus and thus
        this attribute will always be true.
        """
        try:
            return self._element.is_selected()
        except ElementNotSelectableException:
            return False

    @property
    def position(self):
        """
        Element's position.
        """
        pos = self._element.location
        return Position(**pos)

    @property
    def shape(self):
        """
        Element's shape.
        """

        shape = self._element.size
        return Shape(**shape)

    @property
    def text(self):
        """
        Text content for element. Strips HTML tags.
        """
        return self._element.text

    @lazy
    def tag(self):
        """
        HTML tag name for element.
        """
        return self._element.tag_name

    tag_name = property(lambda x: x.tag)

    # Cached attributes
    @lazy
    def _fillable(self):
        return self.tag in FILL_TAGS_WHITELIST

    def __init__(self, element, driver=None):
        self._element = element
        if driver is None:
            driver = element._parent.sulfur
        self._driver = driver

    def __repr__(self):
        # Important attrs
        attrs = []
        if self.id:
            attrs.append('id="#%s"' % self.id)
        attrs = ' '.join(attrs)
        if attrs:
            attrs = ' ' + attrs

        # Data
        data = ''
        if self.text:
            data = ': %r' % self.text
        return '<%s%s%s>' % (self.tag, attrs, data)

    def click(self):
        """
        Clicks the element.
        """
        self.selenium.click()

    def fill(self, text):
        """
        Fill input element with the given text string.
        """
        self._assure_can_fill()
        self._element.send_keys(text)

    def clear(self):
        """
        Clear any input text present in element.
        """
        self._assure_can_fill()
        self._element.clear()

    def attr(self, name, **kwargs):
        """
        Return or set element's attribute.

        Usage:

        elem.attr('attr-name'):
            Return the value of attribute
        elem.attr({'foo': 'bar', 'spam': 'eggs'}):
            Sets the values of all attributes on dictionary.
        elem.attr(foo=bar, spam=eggs):
            Sets attribute values. Underscores on attribute names are converted
            to dashes.
        """

        if not kwargs and isinstance(name, str):
            return self._element.get_attribute(name)
        raise NotImplementedError

    def attribute(self, name, **kwargs):
        """
        Alias to self.attr()
        """

        return self.attr(name, **kwargs)

    def prop(self, name=None, **kwargs):
        """
        Return or set element's property.

        elem.prop('prop-name'):
            Return the value of property
        elem.prop({'foo': 'bar', 'spam': 'eggs'}):
            Sets the values of all properties on dictionary.
        elem.prop(foo=bar, spam=eggs):
            Sets each named property.
        """

        se_element = self._element
        if not kwargs and isinstance(name, str):
            return js_to_python(se_element.get_property(name))

        # Collect new property values
        if name:
            kwargs = dict(name, **kwargs)

        # Execute
        exec = self._driver.selenium.execute_script
        for name, value in kwargs.items():
            value = python_to_js(value)
            exec('arguments[0][%r]=arguments[1];' % name, se_element, value)

    def property(self, name, **kwargs):
        """
        Alias to self.prop()
        """

        return self.prop(name, **kwargs)

    def css(self, name=None, **kwargs):
        """
        Return or set a CSS property.

        Usage:
        elem.css('prop-name'):
            Return the value of given CSS property
        elem.css({'foo': 'bar', 'spam': 'eggs'}):
            Sets the values of all CSS properties on dictionary.
        elem.css(font_family=bar, spam=eggs):
            Sets each named CSS property. Underscores on property names are
            converted to dashes.

        Example:

        >>> elem.css({
        ...     'font-family': 'Helvetica',
        ...     'padding': '20px';
        ... })
        """

        if not kwargs and isinstance(name, str):
            return self._element.value_of_css_property(name)
        raise NotImplementedError

    def method(self, name, *args):
        """
        Calls method with the given arguments.
        """
        args = python_to_js(args)
        js = (
            'var func = arguments[0][arguments[1]];'
            'return func.apply(arguments[0], arguments[2]);'
        )
        result = self._driver.script(js, self._element, name, args)
        if isinstance(result, WebElement) and result.id == self.selenium_id:
            return self
        return js_to_python(result)

    # Protected methods
    def _get_selenium_queryset_object(self):
        return self._element

    def _wrap_element(self, element):
        return Element(element, self._driver)

    def _wrap_queryset(self, queryset):
        wrap = self._wrap_element
        return QuerySet([wrap(x) for x in queryset], self)

    # Checks
    def _assure_can_fill(self):
        if not self._fillable:
            raise DoesNotAcceptInputError()


# Register conversions
@python_to_js.register(Element)
def _(x):
    return x.selenium


@js_to_python.register(WebElement) # noqa
def _(x):
    return Element(x)


@contextmanager
def force_id(elem, keep=True):
    """
    Run block of code with a temporary element id.

    If keep=True and element already has an id, it keeps this id inside the with
    block.
    """

    old_id = elem.id
    changed_id = False
    try:
        changed_id = not old_id
        elem.id = old_id or random_id()
        yield
    finally:
        if changed_id:
            elem.id = old_id
