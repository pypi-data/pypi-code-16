import io

import requests
from bs4 import BeautifulSoup
from lazyutils import lazy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sulfur.conversions import js_to_python
from sulfur.driver_attributes import WindowManager, FocusManager, CookieManager
from sulfur.element import Element
from sulfur.errors import NotFoundError
from sulfur.id_manager import IdManager
from sulfur.queriable import QueriableMixin
from sulfur.queryset import QuerySet
from sulfur.utils import normalize_url, select_url, wrap_selenium_timeout_error, \
    find_likely_input, get_driver_class_from_string


class Driver(QueriableMixin):
    """
    The sulfur web driver.

    A simplified interface to the selenium webdriver with simpler method names
    and a few useful extras.

    Args:
        driver:
            If given, can be a string or a Selenium webdriver object. Strings
            must be on the list: "firefox", "chromium".
            Of course you should have the corresponding web browser installed
            in your system.
        home:
            The home page. Driver starts at the home page and the method
            .home() open it.
    """

    _soup_lib = 'html5lib'

    #: Attributes
    @property
    def title(self):
        """
        Page title.
        """

        return self._driver.title

    @lazy
    def cookies(self):
        """
        Access and modify cookies.
        """

        return CookieManager(self)

    @property
    def selenium(self):
        """
        Selenium web driver object.
        """

        return self._driver

    @property
    def Se(self):
        """
        Alias to .selenium
        """

        return self.selenium

    @lazy
    def soup(self):
        """
        A beautiful soup interface to the HTML source code
        """

        if self.page is None:
            return None
        else:
            return BeautifulSoup(self.page, self._soup_lib)

    @property
    def page(self):
        """
        Current page object.
        """

        return self._page

    @property
    def id(self):
        """
        A simplified interface to dom elements with an id.
        """

        return IdManager(self)

    @property
    def version(self):
        """
        Browser's version.
        """

        return self._driver.capabilities['version']

    @property
    def window(self):
        """
        Control window behaviors.
        """

        return WindowManager(self)

    @property
    def switch_to(self):
        """
        Focus manager.
        """

        return FocusManager(self)

    @property
    def is_windowless(self):
        """
        True if driver runs on a windowless mode (e.g., phantomjs).

        For most drivers, this property is False.
        """

        return self._driver.name in ['phantomjs']

    @property
    def url(self):
        """
        Url for the current page.
        """

        return self.selenium.current_url

    def __init__(self, driver='phantomjs', home=None, wait=0):
        # Normalize driver input
        if driver is None:
            driver = 'phantomjs'
        if isinstance(driver, str):
            driver_cls = get_driver_class_from_string(driver)
            driver = driver_cls()

        self._driver = driver
        self._driver.sulfur = self
        self._page = None
        self.home_url = home and normalize_url(home)
        self._driver.implicitly_wait(wait)
        if self.home_url:
            self.open(self.home_url)

    def __call__(self, selector):
        return self.find(selector)

    def __getitem__(self, selector):
        try:
            return self.elem(selector)
        except NoSuchElementException:
            raise KeyError('no element matches selector: %r' % selector)

    def __repr__(self):
        clsname = self.__class__.__name__
        drivername = self._driver.name
        return '<%s(%r): %s>' % (clsname, drivername, self.url or 'no url')

    #: Browser actions
    def open(self, url=''):
        """
        Opens a page in the given url.
        """

        final_url = url = select_url(self.url or self.home_url, url)
        self._driver.get(final_url)

    def back(self, n=1):
        """
        Go back n steps in browser history.
        """

        if n >= 1:
            self._driver.back()
            self.back(n - 1)
        elif n < 0:
            self._driver.forward()
            self.back(n + 1)

    def forward(self, n=1):
        """
        Go forward n steps in browser history.
        """

        self.back(-n)

    def home(self):
        """
        Return to the home page.
        """

        if self.home_url:
            self.open(self.home_url)
        else:
            raise ValueError('no home url is defined')

    def refresh(self):
        """
        Refresh current page.
        """

        self._driver.refresh()

    # User input
    def click(self, selector):
        """
        Clicks in the first element with the given CSS selector.
        """

        self.elem(selector).click()

    def send(self, selector, *args):
        """
        Alias to send_keys().
        """

        return self.send_keys(selector, *args)

    def send_keys(self, selector, *args):
        """
        Send keys to the first element matched by the selector.

        Args:
            selector: a CSS selector
            text: additional arguments are any combination of keys and text

        Example:
            >>> driver.send_keys('#name-input', 'Guido', '<tab>', 'Python')

        This will select the element with id ``#name-input``, type Guido, than
        press the tab key and finally typing Python.
        """
        return self.elem(selector).send_keys(*args)

    # Forms
    def fill_form(self, selector='form', data=None, **kwargs):
        """
        Fill form with given values.
        """

        form = self.elem(selector)
        data = dict(data or {}, **kwargs)
        for ref, value in data.items():
            elem = find_likely_input(form, ref)
            elem.fill(value)

    def submit(self, selector='form', data=None, **kwargs):
        """
        Fills form with data and submit.

        If script cannot find the correct submit button, use fill_form() and
        then click the button yourself.
        """

        self.fill_form(selector, data, **kwargs)
        self.submit_button(selector).click()

    def submit_button(self, selector='form'):
        """
        Return the submission button for form in the given selector.
        """

        form = self.elem(selector)
        result = (
            form.elem('input[type=submit]', raises=False) or
            form.elem('button[form=%r]' % form.id, raises=False) or
            self.elem('button[form=%r]' % form.id, raises=False)
        )
        if result is None:
            raise NotFoundError('could not find button for form.')
        return result

    def script(self, script, *args, async=False):
        """
        Executes JavaScript script.

        Args:
            script (str):
                A string of JavaScript source.
            async (bool):
                Set to True to execute script asynchronously.

        If you are running a script asynchronously and wants to obtain a value
        from JavaScript, simply add a ``return <something>`` to the end of
        the line in your script.

            >>> driver.script('return 40 + 2')
            42
        """

        if async:
            self._driver.execute_async_script(script, *args)
        else:
            return js_to_python(self._driver.execute_script(script, *args))

    def close(self, quit=True):
        """
        Closes the current web browser tab.

        If quit=True, forces the browser to quit even if there are other tabs
        open. Most browsers will quit when there are no tabs left.
        """

        if quit:
            self._driver.quit()
        else:
            self._driver.close()

    def restart(self):
        """
        Restart the web driver and go to the current url.
        """

        self._driver = type(self._driver)()
        self.open(self.url or '')

    # Other
    def screenshot(self, path=None, format='png'):
        """
        Returns a file object holding data for a  screenshot of the current
        screen.

        Args:
            path:
                If given, saves file in the given path. Othewise saves it in
                a BytesIO() stream.
            format:
                One of 'png' or 'base64'

        Returns:
            A file object with the screenshot contents.
        """

        if path:
            F = open(path, 'wb')
        else:
            F = io.BytesIO()

        if format == 'png':
            data = self._driver.get_screenshot_as_png()
        elif format == 'base64':
            data = self._driver.get_screenshot_as_base64()
        else:
            raise ValueError('invalid format: %r' % format)
        F.write(data)
        return F

    def source(self, request=False):
        """
        Page's HTML source code.

        Args:
            request (bool):
                If True, makes a new request to fetch the page directly without
                relying on selenium. The browser may inject HTML into the
                page to make it represent better the DOM and the resulting
                source may not be identical to the page that was acctually
                served by the web server.
        """

        if request:
            data = requests.get(self.url)
            return data.content.decode('utf8')
        else:
            return self._driver.page_source

    # Wait conditions
    @wrap_selenium_timeout_error
    def wait(self, func, timeout=1.0):
        """
        Wait until func(driver) return True.

        Raises a TimeoutError if condition is not met in the given timeout
        interval.
        """

        WebDriverWait(self, timeout).until(func)

    @wrap_selenium_timeout_error
    def wait_title(self, value, timeout=1.0, contains=False):
        """
        Waits until the page title assumes the given value.

        Raises a TimeoutError if condition is not met in the given interval.

        Args:
            value (str):
                expected title
            timeout (float):
                timeout in seconds
            contains (bool):
                If true, checks if title contains the value substring. The
                default behavior is to wait until the title is exactly equal
                the given value string.
        """

        if contains:
            condition = EC.title_contains(value)
        else:
            condition = EC.title_is(value)
        WebDriverWait(self, timeout).until(condition)

    # Private methods
    def _wrap_element(self, element):
        return Element(element, self)

    def _wrap_queryset(self, query):
        wrap = self._wrap_element
        return QuerySet([wrap(x) for x in query], self)

    def _get_selenium_queryset_object(self):
        return self._driver
