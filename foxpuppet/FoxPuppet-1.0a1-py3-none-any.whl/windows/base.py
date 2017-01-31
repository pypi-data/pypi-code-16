# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class BaseWindow(object):

    _document_element = (By.CSS_SELECTOR, ':root')

    def __init__(self, selenium, handle):
        self.selenium = selenium
        self.handle = handle
        self.wait = WebDriverWait(self.selenium, timeout=10)

    @property
    def document_element(self):
        """ Returns the inner DOM window element.

        :returns: DOM window element.
        """

        return self.selenium.find_element(*self._document_element)

    @property
    def firefox_version(self):
        """ Major version of Firefox in use.

        :returns: Major component of the Firefox version.
        :rtype: int
        """
        version = self.selenium.capabilities['browserVersion']
        return int(version.partition('.')[0])

    def close(self):
        """Closes the window"""

        self.switch_to()
        self.selenium.close()

    def switch_to(self):
        """Switches to the window"""

        self.selenium.switch_to.window(self.handle)
