import time
from random import choice
from string import ascii_lowercase, ascii_letters, digits, punctuation

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tempemail import Mailbox

__author__ = 'sonar235'


def __get_driver():
    driver = webdriver.Chrome()
    driver.set_window_size(1680, 1050)
    driver.set_window_position(0, 0)
    return driver

def __input_user(driver):
    char_pool = ascii_lowercase + digits
    while True:
        username = ''
        while len(username) <= 39:
            next_key = choice(char_pool)
            username += next_key
            driver.find_element_by_id('user_login').send_keys(next_key)
            time.sleep(0.5)
            try:
                driver.find_element_by_class_name('is-autocheck-successful')
                return username
            except NoSuchElementException:
                pass
        driver.find_element_by_id('user_login').clear()


def __input_email(driver):
    box = Mailbox()
    driver.find_element_by_id('user_email').send_keys(box.address)
    return box.address


def __input_password(driver):
    chars = ascii_letters + digits + punctuation
    password = ''.join([choice(chars) for _ in range(16)])
    driver.find_element_by_id('user_password').send_keys(password)
    return password


def __finish_login(driver):
    driver.find_element_by_id('signup_button').click()
    time.sleep(0.5)
    driver.find_element_by_class_name('js-choose-plan-submit').click()
    time.sleep(0.3)
    driver.find_element_by_class_name('alternate-action').click()


def githubreg():
    url = 'https://github.com/join?source=header-home'
    driver = __get_driver()
    driver.get(url)
    user = __input_user(driver)
    print('DID THE USER')
    email = __input_email(driver)
    print('DID THE EMAIL')
    password = __input_password(driver)
    print('DID THE PASSWORD')
    __finish_login(driver)
    driver.quit()
    return user, email, password


if __name__ == '__main__':
    print(githubreg())
