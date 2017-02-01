import getpass
import json
import sys
import time
from datetime import datetime as dt

import argparse
import selenium
from lxml import html
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys


class FSUBot(object):
    TIME_FORMAT = r'%Y-%m-%d-%H-%M-%S'
    FSU_LOGIN_URL = 'https://cas.fsu.edu/cas/login?service=https://my.fsu.edu'

    def __init__(self, fsuid='', fsupw='', command_line=False, auto_login=True, browser={'title': 'firefox', 'path': './'}, description='Bot made using FSU Bot library.'):
        self.SLEEP_TIME = 1.5

        if command_line or (not fsuid and not fsupw):
            parser = FSUBot.ArgParser(description=description)
            self._args = parser.parse()

        if hasattr(self, 'args') and command_line:
            self.fsuid = args.fsuid
        elif fsuid:
            self.fsuid = fsuid
        else:
            self.fsuid = input('FSU-ID: ')

        if hasattr(self, 'args') and command_line:
            self.fsupw = args.fsupw
        elif fsupw:
            self.fsupw = fsupw
        else:
            self.fsupw = getpass.getpass()

        try:
            if browser['title'].lower() == 'firefox':
                binary = FirefoxBinary(browser['path'])
                self.dr = webdriver.Firefox(firefox_binary=binary)
            elif browser['title'].lower() == 'chrome':
                self.dr = webdriver.Chrome(browser['path'])
        except (AttributeError, selenium.common.exceptions.WebDriverException, AttributeError) as e:
            print("ERROR \"{}\": Likely no driver was found.".format(str(e).strip()))
            sys.exit()

        if auto_login:
            self.my_fsu_login()

    def login_to_fsu(self):
        self.dr.get(FSUBot.FSU_LOGIN_URL)
        username = self.dr.find_elements_by_class_name("loginInput")[0]
        password = self.dr.find_elements_by_class_name("loginInput")[1]

        time.sleep(self.SLEEP_TIME)
        print("Entering login credentials...")

        username.send_keys(self.fsuid)
        password.send_keys(self.fsupw)
        time.sleep(self.SLEEP_TIME)

        print("Attempting to login...")
        login_button = '#fm2 > table > tbody > tr:nth-child(2) > td:nth-child(6) > input'
        self.dr.find_elements_by_css_selector(login_button)[0].click()
        time.sleep(self.SLEEP_TIME * 2)

    def navigate(self, filename=None, jsonlist=None):
        if filename:
            with open(filename) as f:
                json_list = json.load(f)

        if json_list:
            for item in json_list:
                self._navigate(**item)
        else:
            raise RuntimeError('No JSON list of navigation points provided.')

    def _navigate(self, title=None, xpath=None, css_selector=None):
        time.sleep(self.SLEEP_TIME * 2)
        if title:
            print("Navigating to " + title + "...")

        if xpath:
            elem = self.dr.find_elements_by_xpath(xpath)[0]
        elif css_selector:
            elem = self.dr.find_elements_by_css_selector(css_selector)[0]
        else:
            raise Exception("Unable to navigate without xpath or " \
                            "css selector.")
        elem.click()

        if title:
            print("Navigation succeeded.")

    def _focus_iframe(self, title, xpath=None, css_selector=None):
        if title:
            print("Focusing on " + title + "'s iFrame...")
        if xpath:
            frame = self.dr.find_elements_by_xpath(xpath)[0]
        elif css_selector:
            frame = self.dr.find_elements_by_css_selector(css_selector)[0]
        self.dr.switch_to.frame(frame)
        print("Frame-switch succeeded.")
        time.sleep(self.SLEEP_TIME)


    def main_loop(self):
        pass

    @property
    def page_source(self):
        return self.dr.page_source.encode('utf-8')

    def element_exists(self, xpath):
        try:
            return bool(self.dr.find_elements_by_xpath(xpath))
        except:
            return False

    class ArgParser(argparse.ArgumentParser):
        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)
            self.add_argument('-f', '--fsu-id',
                              help='Username for the student\'s MyFSU account.',
                              required=False)
            self.add_argument('-p', '--password',
                              help='Password for the student\'s MyFSU account.',
                              required=False)

        def parse(self, *args, **kwargs):
            args = self.parse_args(*args, **kwargs)

            if args.fsu_id and not args.password:
                parser.error('MyFSU ID given, but no password specified.')
            elif not args.fsu_id and args.password:
                parser.error('MyFSU password given, but no ID specified.')

            return args



def _main(nav_list_json=None, main_loop=None):
    """
    :param nav_list: list of
    :type nav_list: list

    """
    fsu_dr = FSUBot(browser={'title':'chrome', 'path':'./chromedriver'})
    fsu_dr.login_to_fsu()
    #fsu_dr.navigate(filename=nav_list_json)
    #fsu_dr.main_loop()


if __name__ == "__main__":
    _main()
