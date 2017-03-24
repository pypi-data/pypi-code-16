import collections

from sulfur.element import Element
from sulfur.utils import Shape, Position


class DriverAttributeMixin:
    """
    Base class for several driver attributes.
    """

    def __init__(self, driver):
        self._parent = driver
        self._driver = driver.selenium

    def _wrap_element(self, el):
        if el is None:
            return None
        return Element(el, self._parent)


class WindowManager(DriverAttributeMixin):
    """
    Driver .window attribute.
    """

    @property
    def shape(self):
        """
        Window shape as a (width, height) tuple.
        """
        shape = self._driver.get_window_size()
        return Shape(**shape)

    @shape.setter
    def shape(self, value):
        width, height = value
        self._driver.set_window_size(width, height)

    @property
    def position(self):
        pos = self._driver.get_window_position()
        return Position(**pos)

    @position.setter
    def position(self, value):
        x, y = value
        self._driver.set_window_position(x, y)

    def maximize(self):
        """
        Maximizes browser window.
        """

        self._driver.maximize_window()

    def minimize(self):
        """
        Minimizes browser window.
        """

        raise NotImplementedError
        self._driver.minimize_window()


class FocusManager(DriverAttributeMixin):
    """
    Driver .switch_to attribute.
    """

    def active(self):
        """
        Focus on active element.

        Selects page <body> if no elemente is active.
        """

        return self._wrap_element(self._driver.switch_to)

    def alert(self):
        """
        Focus on an alert on page.
        """

        return self._wrap_element(self._driver.switch_to.alert)

    def default_frame(self):
        """
        Focus on default frame.
        """

        return self._wrap_element(self._driver.switch_to.default_content())

    def frame(self, reference):
        """
        Focus on specific frame.

        Reference can be a name, an index or an element.
        """

        return self._driver.switch_to.frame(reference)

    def window(self, name='main'):
        """
        Switch to window specified by name.
        """

        return self._wrap_element(self._driver.switch_to.window(name))


class CookieManager(DriverAttributeMixin, collections.Sequence):
    """
    Driver .cookies attribute.
    """

    @property
    def _data(self):
        return self._driver.get_cookies()

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._driver.get_cookie(key)
        else:
            return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __setitem__(self, key, value):
        self.create(key, value)

    def __delitem__(self, key):
        self._driver.delete_cookie(key)

    def clear(self):
        """
        Remove all cookies.
        """

        self._driver.delete_all_cookies()

    def create(self, name=None, D=None, **kwargs):
        """
        Creates a new cookie with the given name.
        """

        if name is not None:
            kwargs['name'] = name
        if D is not None:
            kwargs = dict(D, **kwargs)
        return self._driver.add_cookie(kwargs)
