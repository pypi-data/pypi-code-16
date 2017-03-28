from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pySMS.html.pathdata.loginPage as lp
import time


class Waits():

    def __init__(self, selenium_driver, time_out=10):

        self.driver = selenium_driver
        self.time_out = time_out

    def implicit(self, time=10):
        self.driver.implicitly_wait(time)

    @staticmethod
    def sleep(n):
        time.sleep(n)

    def to_exist(self, selection_input, find_by=By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.driver, self.time_out).until(
                EC.presence_of_element_located((find_by, selection_input))
            )
            return selection_input
        except:
            print('Unable to find element. [{}]'.format(str(selection_input)))
            raise Exception

    def clickable(self, selection_input, find_by=By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.driver, self.time_out).until(
                EC.element_to_be_clickable((find_by, selection_input))
            )
            element.click()
        except Exception as e:
            print('Unable to click element. [{}]'.format(str(selection_input)))
            raise Exception

    def send_keys_to(self, text, selection_input, find_by=By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.driver, self.time_out).until(
                EC.element_to_be_clickable((find_by, selection_input))
            )
            element.send_keys(text)
        except:
            print('Unable to send keys to element. [{}]'.format(str(selection_input)))
            raise Exception

    def clear_input(self, selection_input, find_by=By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.driver, self.time_out).until(
                EC.element_to_be_clickable((find_by, selection_input))
            )
            element.clear()
        except:
            print('Unable to clear to element. [{}]'.format(str(selection_input)))
            raise Exception
