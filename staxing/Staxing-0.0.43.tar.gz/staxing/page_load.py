"""
Wait for page load in Selenium.

credit to Tommy Beadle for the solution and
http://www.obeythetestinggoat.com/
how-to-get-selenium-to-wait-for-page-load-after-a-click.html
"""

from contextlib import contextmanager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

__version__ = '0.0.3'


class SeleniumWait(object):
    """Wait for webpage load by watching for staleness."""

    def __init__(self, driver, wait):
        """Constructor."""
        self.browser = driver
        self.wait = wait
        self.pseudos = [
            '::after', '::before', '::first-letter', '::first-line',
            '::selection', '::backdrop', '::placeholder', '::marker',
            '::spelling-error', '::grammar-error'
        ]

    @contextmanager
    def wait_for_page_load(self):
        """Delay progress until the new page is available."""
        old_page = self.browser.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.browser, self.wait).until(
            staleness_of(old_page)
        )

    @contextmanager
    def wait_for_loading_staleness(self, style, pseudo_element):
        """Wait for section load.

        Parameters:
            style <str>: element CSS style
            pseudo <str>: CSS pseudo-element selector
                '::after'
                '::before'
                '::first-letter'
                '::first-line'
                '::selection'
                '::backdrop'
                '::placeholder'
                '::marker'
                '::spelling-error'
                '::grammar-error'
        """
        pseudo, pseudo_is_valid = self.is_valid_pseudo(pseudo_element)
        if not pseudo_is_valid:
            raise ValueError('%s not in %s' % (self.pseudos))
        WebDriverWait(self.driver, 90).until(
            staleness_of(
                self.driver.find_element(
                    By.CSS_SELECTOR,
                    '%s%s' % (style, pseudo)
                )
            )
        )

    def is_valid_pseudo(self, pseudo_element):
        """Validate pseudo selector."""
        pseudo = ''.join(('::', pseudo_element.split(':')[-1]))
        return (pseudo, pseudo in self.pseudos)
