# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from selenium.common.exceptions import TimeoutException

from foxpuppet.windows.browser.notifications import BaseNotification
from foxpuppet.windows.browser.notifications.addons import (
    AddOnInstallBlocked,
    AddOnInstallComplete,
    AddOnInstallConfirmation)


@pytest.fixture
def firefox_options(firefox_options):
    # Due to https://bugzilla.mozilla.org/show_bug.cgi?id=1329939 we need the
    # initial browser window to be in the foreground. Without this, the
    # notifications will not be displayed.
    firefox_options.add_argument('-foreground')
    return firefox_options


@pytest.fixture
def addon():
    class AddOn(object):
        name = 'WebExtension'
        path = 'webextension.xpi'
    return AddOn()


@pytest.fixture
def blocked_notification(addon, browser, webserver, selenium):
    selenium.get(webserver.url())
    selenium.find_element_by_link_text(addon.path).click()
    return browser.wait_for_notification(AddOnInstallBlocked)


@pytest.fixture
def confirmation_notification(browser, blocked_notification):
    blocked_notification.allow()
    return browser.wait_for_notification(AddOnInstallConfirmation)


def test_open_close_notification(browser, blocked_notification):
    """Trigger and dismiss a notification"""
    assert blocked_notification is not None
    blocked_notification.close()
    return browser.wait_for_notification(None)


@pytest.mark.parametrize('_class, message', [
    (BaseNotification, 'No notification was shown'),
    (AddOnInstallBlocked, 'AddOnInstallBlocked was not shown')])
def test_wait_for_notification_timeout(browser, _class, message):
    """Wait for a notification when one is not shown"""
    with pytest.raises(TimeoutException) as excinfo:
        browser.wait_for_notification(_class)
    assert message in str(excinfo.value)


def test_wait_for_no_notification_timeout(browser, blocked_notification):
    """Wait for no notification when one is shown"""
    with pytest.raises(TimeoutException) as excinfo:
        browser.wait_for_notification(None)
    assert 'Unexpected notification shown' in str(excinfo.value)


def test_notification_with_origin(browser, webserver, blocked_notification):
    """Trigger a notification with an origin"""
    assert '{0.host}:{0.port}'.format(webserver) in blocked_notification.origin
    assert blocked_notification.label is not None


def test_allow_blocked_addon(browser, blocked_notification):
    """Allow a blocked add-on installation"""
    blocked_notification.allow()
    browser.wait_for_notification(AddOnInstallConfirmation)


def test_cancel_addon_install(browser, confirmation_notification):
    """Cancel add-on installation"""
    confirmation_notification.cancel()
    browser.wait_for_notification(None)


def test_confirm_addon_install(addon, browser, confirmation_notification):
    """Confirm add-on installation"""
    assert confirmation_notification.addon_name == addon.name
    confirmation_notification.install()
    browser.wait_for_notification(AddOnInstallComplete)
