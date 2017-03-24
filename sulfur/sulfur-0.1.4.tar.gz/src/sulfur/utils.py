import collections
import functools
import string
from random import choice

import selenium.common.exceptions


def normalize_url(url):
    """
    Forces url to have a correct protocol specification.

    Examples:
        >>> normalize_url('google.com')
        'http://google.com'
    """

    if '://' not in url:
        return 'http://' + url
    return url


def select_hostname(url):
    """
    Return hostname from url.

    Examples:
        >>> select_hostname('http://python.org/about.html')
        'python.org'
        >>> select_hostname('python.org/foo')
        'python.org'
    """
    protocol, sep, host = url.rpartition('://')
    return host.partition('/')[0]


def select_url(base_url, new_url):
    """
    Select final URL from current url and new url fragment.
    """

    # Check if url starts with http://... This is a fully normalized url.
    protocol, sep, host = new_url.rpartition('://')
    if protocol:
        return new_url

    # Fetch absolute url from host
    if new_url.startswith('/'):
        protocol, sep, host = base_url.rpartition('://')
        return '%s://%s%s' % (protocol, select_hostname(base_url), new_url)

    # Fetches relative url
    else:
        protocol, sep, url = base_url.rpartition('://')
        url = url.rpartition('/')[0]
        if protocol:
            url = '%s://%s' % (protocol, url)
        return normalize_url('%s/%s' % (url, new_url))


def random_id():
    """
    Return a random string of text that can be used as an id.
    """

    return ''.join(choice(c) for c in string.ascii_letters)


def wrap_selenium_timeout_error(func):
    """
    Decorator that wraps a function that may emmit a selenium timeout error to
    use Python's native TimeoutError.
    """

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except selenium.common.exceptions.TimeoutException as ex:
            raise TimeoutError(ex)

    return decorated


#
# Special types
#
_Shape = collections.namedtuple('Shape', ['width', 'height'])
_Position = collections.namedtuple('Position', ['x', 'y'])


class Position(_Position):
    """
    Represents screen positions.
    """

    def __add__(self, other):
        x, y = other
        return Position(x=self.x + x, y=self.y + y)

    def __sub__(self, other):
        x, y = other
        return self.__add__((-x, -y))


class Shape(_Shape):
    """
    Represents rectangular shapes with given width and height.
    """

    def rescale(self, scale):
        """
        Returns a copy rescaled by the given scale factor.
        """

        return Shape(scale * self.x, scale * self.y)


def find_likely_input(form, ref):
    """
    Return the likely input element with the given reference.
    """

    # Fetch by id in the whole document
    driver = form._driver
    if ref.startswith('#'):
        return driver.elem(ref)

    # If it fails, tries to fetch by id (adding a # symbl) inside the form
    result = (
        form.elem('#' + ref, raises=False) or
        form.elem('[name=%s]' % ref, raises=False) or
        driver.elem('#' + ref, raises=False) or
        driver.elem('[name=%s]' % ref, raises=False)
    )
    if result is None:
        raise ValueError('could not find element %s on form' % ref)
    return result


def get_driver_class_from_string(name):
    """
    Select driver class from name.
    """

    mapping = {
        'firefox': 'selenium.webdriver.Firefox',
        'chrome': 'selenium.webdriver.Chrome',
        'ie': 'selenium.webdriver.Ie',
        'edge': 'selenium.webdriver.Edge',
        'opera': 'selenium.webdriver.Opera',
        'safari': 'selenium.webdriver.Safari',
        'blackberry': 'selenium.webdriver.BlackBerry',
        'phantomjs': 'selenium.webdriver.PhantomJS',
        'android': 'selenium.webdriver.Android',
    }

    mod, _, cls = mapping[name].rpartition('.')
    mod = __import__(mod, fromlist=[cls])
    return getattr(mod, cls)