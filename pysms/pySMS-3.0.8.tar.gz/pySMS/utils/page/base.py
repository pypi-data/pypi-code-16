from selenium import webdriver
import pySMS.html.pathdata.loginPage as lp
import os

class Page:
    """
    Base class that all page models can inherit from
    """

    @staticmethod
    def create_driver(path_to_driver):
        chromedriver = path_to_driver
        os.environ["webdriver.chrome.driver"] = chromedriver
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        driver = webdriver.Chrome(chromedriver)

        return driver, driver.command_executor._url, driver.session_id
