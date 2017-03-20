#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
#  vim: set ts=4 sw=4 tw=79 et :
"""A script to scrape all images and videos from a Facebook profile.

fbscraper.py will go through all albums of a Facebook profile and proceed to
download them one by one.

"""
import os
import argparse
import sqlite3
import time
import logging

import requests
import pyvirtualdisplay
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Facebook(object):

    DEBUG = False

    def __init__(self, email=None, passwd=None):
        self.email = email
        self.passwd = passwd
        self.base_url = "https://fb.com"

        self.conn = sqlite3.connect("db.sqlite")
        self.cur = self.conn.cursor()
        self.session = requests.Session()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS links
                            (link text PRIMARY KEY)''')

        if Facebook.DEBUG:
            logging.basicConfig(level=logging.DEBUG)

        self.start_browser()

        if email is not None and passwd is not None:
            self.login()

    def start_browser(self):
        """Starts the headless browser."""
        chrome_options = webdriver.ChromeOptions()
        my_preferences = {
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", my_preferences)

        display = pyvirtualdisplay.Display(visible=0, size=(1024, 768))
        display.start()
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    def login(self):
        """Logs into facebook.com."""
        self.browser.get(self.base_url)

        email_field = self.browser.find_element_by_name("email")
        email_field.send_keys(self.email)
        pass_field = self.browser.find_element_by_name("pass")
        pass_field.send_keys(self.passwd)

        pass_field.submit()

    def albums(self, account_id: str) -> list:
        """Scrape the links to the public albums of the user.

        Args:
            account_id: the account identifier which can be found in the account
            url
        """
        account_url = "{}/{}".format(self.base_url, account_id)
        self.browser.get(account_url)

        self.browser.find_element_by_xpath(
             "//*[@data-tab-key='photos']").click()
        time.sleep(5)
        self.browser.find_element_by_xpath("//a[. = 'Albums']").click()
        time.sleep(5)

        albums = (self.browser.find_elements_by_xpath(
                 "//*[@class='photoTextTitle']"))
        albums = {i.text: i.get_attribute("href") for i in albums}

        return albums

    def insert_row(self, url: str) -> sqlite3.Cursor:
        """Inserts a row into our database.

        Args:
            url: the url which we've already scraped

        """
        return self.cur.execute("INSERT INTO links(link) VALUES (?)", [url])

    def download(self, url: str, dir_: str,
                 user: str, timestamp: str) -> None:
        """Downloads the item.

        Args:
            url: the url where our item is
            directory: which directory to save the item to
            user: the name of the user we're scraping
            timestamp: timestamp when the item was uploaded

        """
        if url.startswith("https://video"):
            ext = "mp4"
        else:
            ext = "jpg"

        req = self.session.get(url, stream=True)
        filename = "{}/{}-{}.{}".format(dir_, user, timestamp, ext)

        with open(filename, "wb") as fp:
            for chunks in req.iter_content(1024):
                fp.write(chunks)

    def scrape_images(self, account_id: str, dir_: str, wait: int=4) -> None:
        """Scrape all the links to the images and videos.

        Args:
            account_id: the account identifier which can be found in the account
            url
            wait: how many seconds to wait between downloads

        """
        albums = self.albums(account_id)

        for name, url in albums.items():
            self.browser.get(url)

            if name == "Videos":
                item_url = (self.browser.find_element_by_xpath(
                            "//*[@aria-label='Video']"))
            else:
                item_url = (self.browser.find_element_by_xpath(
                            "//a[contains(@class, 'uiMediaThumbMedium')]"))

            item_url.click()
            time.sleep(wait)

            while True:
                time.sleep(wait)

                if name == "Videos":
                    item_url = self.browser.find_element_by_xpath("//video")
                else:
                    item_url = (self.browser.find_element_by_xpath(
                               "//img[@class='spotlight']"))

                item_url = item_url.get_attribute("src")

                user = (self.browser.find_element_by_xpath(
                       "//div[@class='fbPhotoContributorName']/a"))
                user = user.text

                upload_timestamp = (self.browser.find_element_by_xpath(
                                   "//span[@id='fbPhotoSnowliftTimestamp']"
                                   "//abbr"))
                upload_timestamp = upload_timestamp.get_attribute("data-utime")

                try:
                    self.insert_row(self.browser.current_url)
                except sqlite3.IntegrityError:
                    break

                self.download(item_url, dir_,
                              user, upload_timestamp)
                self.conn.commit()

                next_image = self.browser.find_element_by_tag_name("body")
                next_image.send_keys(Keys.RIGHT)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-u", "--user",
                        help="account to log into before downloading items",
                        required=False)
    parser.add_argument("-p", "--passwd",
                        help="password to the supplied account",
                        required=False)
    parser.add_argument("-i", "--id",
                        help="user id of the account to scrape", required=True)
    parser.add_argument("-o", "--output", help="output destination",
                        required=False, default="fbscraper_images")
    args = parser.parse_args()

    if args.output:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

    fb = Facebook(args.user, args.passwd)
    fb.scrape_images(args.id, args.output)
