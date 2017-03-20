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
    DEFAULT_WEBDRIVER_WAIT_TIME = 10

    def __init__(self, *args, **kwargs):
        """
        :param use_cli: Decision to look for/make use of provided CLI arguments.
        :param modify_arg_parser: Instantiate a bot, but do not initialize
            immediately. This allows developer to add custom CLI arguments
            (which are then passed to initialize).
        """
        self.arg_parser = FSUBot.ArgParser()

        if kwargs.get('modify_arg_parser'):
            print("Parser provided as `self.arg_parser`. Automatic arguments "
                  "for ID, password, browser, and executable-path have been "
                  "added.\nCall `FSUBot.initialize` and pass the unpacked "
                  "return value from self.arg_parser.parse_args.")
        else:
            if kwargs.get('use_cli'):
                self.initialize(*args, **self.arg_parser.parse_args(), **kwargs)
            else:
                self.initialize(*args, **kwargs)

    @selenium_safe_run
    def initialize(self, *args, **kwargs):
        """
        :param driver: Instance of selenium driver already instantiated.
        :param executable_path: Path to the driver/executable to instantiate
            the selenium driver with.
        :param fsuid: FSU-ID to use when logging into MyFSU.
        :param password: Password to use when logging into MyFSU.
        :param use_cli: Decision to look for/make use of provided CLI arguments.
        :param auto_login: Decision to automatically login to MyFSU.
        :param browser: Name of actual browser ('chrome' or 'firefox')
        :param description: Description associated with the bot.
        :param verbose: Decision to print more verbose logging messages.
        :param sleep_time: Adjust based on connection speed, time between actions.
        """
        driver          = kwargs.get('driver', None)
        executable_path = kwargs.get('executable_path')
        fsuid           = kwargs.get('fsuid')
        password        = kwargs.get('password')
        use_cli         = bool(kwargs.get('use_cli', False))
        auto_login      = kwargs.get('auto_login', True)
        browser         = kwargs.get('browser', 'chrome')
        description     = kwargs.get('description', 'An FSU Bot.')
        self.VERBOSE    = kwargs.get('verbose', True)
        self.SLEEP_TIME = int(kwargs.get('sleep_time', 1.5))

        self.fsuid      = fsuid    if isinstance(fsuid, str)    and fsuid    else input('FSU-ID: ')
        self.password   = password if isinstance(password, str) and password else getpass.getpass()

        FIREFOX_NAMES = ('firefox', 'gecko', 'geckodriver', 'firefoxdriver')
        CHROME_NAMES  = ('chrome', 'chromedriver', 'googlechrome')

        if driver:
            self.dr = driver
        else:
            try:
                if browser in FIREFOX_NAMES:
                    self.dr = webdriver.Firefox(
                        firefox_binary=FirefoxBinary(executable_path)
                    ) if executable_path else webdriver.Firefox()
                elif browser in CHROME_NAMES:
                    self.dr = webdriver.Chrome(
                        executable_path=executable_path
                    ) if executable_path else webdriver.Chrome()
                else:
                    raise RuntimeError("\"No valid webdriver-identifying name provided\", bailing.")
            except WebDriverException as e:
                print("\"{}\": Bailing.".format(str(e).strip()))
                sys.exit()

        self.WAIT = ui.WebDriverWait(self.dr, FSUBot.DEFAULT_WEBDRIVER_WAIT_TIME)

        if auto_login:
            self.login_to_fsu()

    @selenium_safe_run
    def login_to_fsu(self):
        self.vprint("Navigating to login page...")
        self.dr.get(FSUBot.FSU_LOGIN_URL)
        self.WAIT.until(lambda driver: driver.find_element_by_xpath(
            '//*[@id="username"]'
        ))

        self.vprint("Entering login credentials...")
        username = self.dr.find_elements_by_id("username")[0]
        password = self.dr.find_elements_by_id("password")[0]
        username.send_keys(self.fsuid)
        password.send_keys(self.password)

        login_button = '#fsu-login-button'
        self.dr.find_elements_by_css_selector(login_button)[0].click()
        self.vprint("Clicked login button.")
        self.WAIT.until(lambda driver: driver.find_element_by_xpath(
            '//*[@id="fsuMyCoursesCurrentTab"]/a'
        ))
        self.vprint("Successfully logged into MyFSU.")

    @selenium_safe_run
    def click_list(self, filename=None, list_key=None, json_list=None):
        """
        :filename: relative to script filename of json file containing
            json_list (requires list_key)
        :param json_list: list of pre-defined format page dictionaries
            containing a title and either xpath or a css_selector
        :param list_key: key for list containing pages within json
        """
        if filename and list_key:
            if filename[0] != '/':
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
                    self._click(**page)
                time.sleep(self.SLEEP_TIME)
        else:
            raise RuntimeError('No JSON list of elements provided.')

    @selenium_safe_run
    def _click(self, title=None, xpath=None, css_selector=None):
        if title:
            self.vprint("Locating " + title + "...")

        if xpath:
            elem = self.dr.find_elements_by_xpath(xpath)[0]
        elif css_selector:
            elem = self.dr.find_elements_by_css_selector(css_selector)[0]
        else:
            raise Exception("Unable to locate element without xpath or " \
                            "css selector.")
        elem.click()
        self.vprint("Click succeeded.")

    @selenium_safe_run
    def _focus_iframe(self, title, xpath=None, css_selector=None):
        if title:
            self.vprint("Focusing on " + title + "'s iFrame...")

        if xpath:
            frame = self.dr.find_elements_by_xpath(xpath)[0]
        elif css_selector:
            frame = self.dr.find_elements_by_css_selector(css_selector)[0]
        else:
            raise Exception("Unable to locate element without xpath or " \
                            "css selector.")

        self.dr.switch_to.frame(frame)
        self.vprint("Frame-switch succeeded.")

    def vprint(self, *args, **kwargs):
        if self.VERBOSE:
            print(*args, **kwargs)

    @staticmethod
    def _make_path_relative(relative_path):
        """
        :param relative_path: accepts a relative path and makes it
            absolute with respect to the script's location
        """
        return str(
            os.path.join(
                os.path.abspath(os.path.dirname(sys.argv[0])),
                relative_path
            )
        )

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
            self.add_argument('-p', '--password', dest="password",
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

            if _args.fsuid and not _args.password:
                parser.error('MyFSU ID given, but no password specified.')
            elif not _args.fsuid and _args.password:
                parser.error('MyFSU password given, but no ID specified.')

            return dict(_args._get_kwargs())


def _main():
    fsu_dr = FSUBot(use_cli=True)


if __name__ == "__main__":
    _main()
