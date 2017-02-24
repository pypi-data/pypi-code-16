# -*- coding: utf-8 -*-
from splinter import Browser
import os
import webbrowser
import tempfile
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
basedir = os.path.abspath(os.path.dirname(__file__))


def start_browser(browser='firefox'):

    if browser == 'chrome':
        chrome_path = os.path.join(basedir,
                                   'webdrivers/chromedriver')
        browser = Browser('chrome', executable_path=chrome_path)
    elif browser == 'phantomjs':
        phantomjs_path = os.path.join(basedir,
                                      'webdrivers/phantomjs')
        browser = Browser(
            'phantomjs',
            executable_path=phantomjs_path,
            user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0',
        )
    elif browser == 'firefox':
        browser = Browser('firefox')
    else:
        raise Exception('Unknown browser')

    browser.driver.maximize_window()
    return browser


def start_webdriver(browser='phantomjs'):

    if browser == 'chrome':
        chrome_path = os.path.join(basedir,
                                   'webdrivers/chromedriver')
        browser = webdriver.Chrome(executable_path=chrome_path)
    elif browser == 'phantomjs':
        phantomjs_path = os.path.join(basedir,
                                      'webdrivers/phantomjs')

        caps = DesiredCapabilities.PHANTOMJS
        caps["phantomjs.page.settings.userAgent"] = \
            ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 "
             "Firefox/48.0")

        browser = webdriver.PhantomJS(executable_path=phantomjs_path,
                                      desired_capabilities=caps)
    else:
        raise Exception('Unknown browser')

    browser.maximize_window()
    return browser


def open_resp(r, browser='chrome'):
    """ Legacy, Do NOT use """

    if browser == 'chrome':
        chrome_path = os.path.join(basedir,
                                   'webdrivers/chromedriver')
        browser = Browser('chrome', executable_path=chrome_path)
        browser.driver.get("data:text/html;charset=utf-8," + r.content)
    elif browser == 'firefox':
        browser = Browser('firefox')
        browser.driver.execute_script("""
                            document.location = 'about:blank';
                            document.open();
                            document.write(arguments[0]);
                            document.close();
                            """, r.content)
    else:
        raise Exception('Unknown browser')
    return browser


def open_in_browser(r, url=None):
    """ r: requests response or html text/unicode
    Open the given response in a local web browser, populating the <base>
    tag for external links to work
    """

    if isinstance(r, requests.Response):
        url = r.url
        body = r.text
    else:
        body = r
    fname = save_html_tmp(body, url)
    return webbrowser.open("file://%s" % fname)


def save_html_tmp(body, url=None):

    if isinstance(body, requests.Response):
        url = body.url
        body = body.text
    if url and '<base' not in body:
        repl = '<head><base href="%s">' % url
        body = body.replace('<head>', repl)
    ext = '.html'
    fd, fname = tempfile.mkstemp(ext)
    os.write(fd, body.encode('utf-8'))
    os.close(fd)
    return fname
