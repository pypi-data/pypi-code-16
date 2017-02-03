import getpass
import json
import os
import sys
import time

import argparse
import selenium
import selenium.webdriver.support.ui as ui
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException


def selenium_safe_run(func):
    """ Exists until this is merged:

    https://github.com/SeleniumHQ/selenium/pull/3452

    """
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return func(*args, **kwargs)
        except selenium.common.exceptions.WebDriverException:
            try:
                self.dr.close()
            except (NameError, AttributeError):
                print("Selenium error. Contact the dev.")
                sys.exit()
    return wrapper

class FSUBot(object):
    TIME_FORMAT = r'%Y-%m-%d-%H-%M-%S'
    FSU_LOGIN_URL = 'https://cas.fsu.edu/cas/login?service=https://my.fsu.edu'

    def __init__(self, *args, **kwargs):
        self.arg_parser = FSUBot.ArgParser()

        if not kwargs.get('modify_arg_parser'):
            if kwargs.get('use_cli'):
                self.initialize(*args, **self.arg_parser.parse_args(), **kwargs)
            else:
                self.initialize(*args, **kwargs)
        else:
            print("Parser provided as `self.arg_parser`. Automatic arguments "
                  "for ID and password have been added.\nCall `FSUBot.setup` "
                  "with the parsed arguments dictionary.")
            self.arg_parser = FSUBot.ArgParser()

    @selenium_safe_run
    def initialize(self, *args, **kwargs):
        driver = kwargs.get('driver', None)
        executable_path = str(kwargs.get('executable_path'))
        fsuid = str(kwargs.get('fsuid', None))
        fsupw = str(kwargs.get('fsupw', None))
        use_cli = bool(kwargs.get('use_cli', False))
        auto_login = kwargs.get('auto_login', True)
        browser = str(kwargs.get('browser', 'chrome'))
        description = str(kwargs.get('description', 'An FSU Bot.'))

        self.VERBOSE = kwargs.get('verbose', True)
        self.SLEEP_TIME = int(kwargs.get('sleep_time', 1.5))

        self.fsuid = fsuid if isinstance(fsuid, str) and fsuid != 'None' else input('FSU-ID: ')
        self.fsupw = fsupw if isinstance(fsupw, str) and fsupw != 'None' else getpass.getpass()

        if not driver:
            try:
                if browser.lower() == 'firefox':
                    if executable_path:
                        self.dr = webdriver.Firefox(
                            firefox_binary=FirefoxBinary(executable_path)
                        )
                    else:
                        self.dr = webdriver.Firefox()
                else:  # browser.lower() == 'chrome':
                    if executable_path:
                        self.dr = webdriver.Chrome(
                            executable_path=executable_path
                        )
                    else:
                        self.dr = webdriver.Chrome()
            except WebDriverException as e:
                print("\"{}\": Bailing.".format(str(e).strip()))
                sys.exit()
        elif driver:
            print("else")
            self.dr = driver
        else:
            raise RuntimeError("Bailing, unable to instantiate a webdriver.")

        self.wait = ui.WebDriverWait(self.dr, 10)
        if auto_login: self.login_to_fsu()

    @selenium_safe_run
    def login_to_fsu(self):
        self.dr.get(FSUBot.FSU_LOGIN_URL)
        self.wait.until(lambda driver: driver.find_element_by_xpath(
            '//*[@id="fm2"]/table/tbody/tr[2]/td[3]/input'
        ))

        self.vprint("Entering login credentials...")
        username = self.dr.find_elements_by_class_name("loginInput")[0]
        password = self.dr.find_elements_by_class_name("loginInput")[1]
        username.send_keys(self.fsuid)
        password.send_keys(self.fsupw)

        self.vprint("Attempting to login...")
        login_button = '#fm2 > table > tbody > tr:nth-child(2) > td:nth-child(6) > input'
        self.dr.find_elements_by_css_selector(login_button)[0].click()
        self.wait.until(lambda driver: driver.find_element_by_xpath(
            '//*[@id="portlet-wrapper-stu_myCourses_WAR_stu_myCourses"]/div[1]/div[1]'
        ))
        self.vprint("Successfully logged into MyFSU.")

    @selenium_safe_run
    def navigate(self, filename=None, list_key=None, json_list=None):
        """
        :filename: relative to script filename of json file containing
            json_list (requires list_key)
        :param json_list: list of pre-defined format page dictionaries
            containing a title and either xpath or a css_selector
        :param list_key: key for list containing pages within json
        """
        if filename and list_key:
            filename = FSUBot._make_path_relative(filename)
            with open(filename) as f:
                json_list = json.load(f)[list_key]

        if isinstance(json_list, list):
            for item in json_list:
                page = {
                    'title': item['title'],
                    'xpath': item['xpath'],
                    'css_selector': item['css_selector']
                }
                if item['iframe']:
                    self._focus_iframe(**page)
                else:
                    self._navigate(**page)
                time.sleep(self.SLEEP_TIME)
        else:
            raise RuntimeError('No JSON list of navigation points provided.')

    @selenium_safe_run
    def _navigate(self, title=None, xpath=None, css_selector=None):
        if title: self.vprint("Navigating to " + title + "...")

        if xpath:
            elem = self.dr.find_elements_by_xpath(xpath)[0]
        elif css_selector:
            elem = self.dr.find_elements_by_css_selector(css_selector)[0]
        else:
            raise Exception("Unable to navigate without xpath or " \
                            "css selector.")
        elem.click()
        self.vprint("Navigation succeeded.")

    @selenium_safe_run
    def _focus_iframe(self, title, xpath=None, css_selector=None):
        if title: self.vprint("Focusing on " + title + "'s iFrame...")

        if xpath:
            frame = self.dr.find_elements_by_xpath(xpath)[0]
        elif css_selector:
            frame = self.dr.find_elements_by_css_selector(css_selector)[0]
        self.dr.switch_to.frame(frame)

        self.vprint("Frame-switch succeeded.")

    def vprint(self, *args, **kwargs):
        if self.VERBOSE:
            print(*args, **kwargs)

    @property
    def page_source(self):
        return self.dr.page_source.encode('utf-8')

    class ArgParser(argparse.ArgumentParser):
        def __init__(self, *args, cli_args=None, **kwargs):
            """
            :param cli_args: method to add additional commandline arguments
            :type cli_args: list of lists containing add_argument parameters as dicts
            """
            super().__init__(*args, **kwargs)
            self.add_argument('-f', '--fsu-id', dest="fsuid",
                              help='Username for the student\'s MyFSU account.',
                              required=False)
            self.add_argument('-p', '--password', dest="fsupw",
                              help='Password for the student\'s MyFSU account.',
                              required=False)
            self.add_argument('-b', '--browser', dest="browser",
                              help="The name of the browser driver.",
                              required=False)
            self.add_argument('-e', '--executable-path', dest="executable_path",
                              help='Path to browser driver/executable.',
                              required=False)

            self._parse_args = lambda p: argparse.ArgumentParser.parse_args(p)

        def parse_args(self, *args, **kwargs):
            _args = self._parse_args(self, *args, **kwargs)

            if _args.fsuid and not _args.fsupw:
                parser.error('MyFSU ID given, but no password specified.')
            elif not _args.fsuid and _args.fsupw:
                parser.error('MyFSU password given, but no ID specified.')

            d = {}
            for k, v in _args._get_kwargs():
                d[k] = v

            return d



def _main():
    fsu_dr = FSUBot(use_cli=True)
    fsu_dr.initialize(**fsu_dr.arg_parser.parse_args())


if __name__ == "__main__":
    _main()
