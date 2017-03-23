from selenium import webdriver
import pySMS.html.pathdata.userSettings as us
import pySMS.html.pathdata.loginPage as lp
from pySMS.utils.page.waits import Waits
import json
import os
import time

class ChangeSite:

    def __init__(self, selenium_driver, username, password):
        self.driver = selenium_driver
        self.username = username
        self.password = password

        self.wait = Waits(selenium_driver)

    @staticmethod
    def load_sites():
        with open(os.path.dirname(os.path.realpath(__file__)) + '\\siteSettings.json', 'r')as j_file:
            sites = json.load(j_file)
        return sites

    @staticmethod
    def get_site_selector(site_dict, site_name):
        for site, data in site_dict['listBoxSites'].items():
            if site == site_name:
                return data['path']

    def change_site(self, site_name, delay=2, login=True):
        formatted_site_name = " ".join(site_name.split("_"))
        _selector = self.get_site_selector(self.load_sites(), site_name)

        try:
            self.wait.clickable(us.upUser)
            self.wait.clickable(us.upUserSettingsButton)
            self.wait.clickable(_selector)
            self.wait.clickable(us.upSaveButton)
        except Exception as e:
            print('Unable to change to site [{:<10s}] Please manually change sites to continue'.format(formatted_site_name))
            print('Exception: [{}]'.format(str(e)))
            input('Press any key to continue')

        self.wait.sleep(delay)
        self.driver.get(self.driver.current_url)

        if login != False:
            try:
                self.wait.send_keys_to(self.username, lp.username)
                self.wait.send_keys_to(self.password, lp.password)
                self.wait.clickable(lp.loginbutton)
            except Exception as e:
                print('Unable to login, Please login manually.')
                print('Exception: [{}]'.format(str(e)))
                input('Press any key to continue')




