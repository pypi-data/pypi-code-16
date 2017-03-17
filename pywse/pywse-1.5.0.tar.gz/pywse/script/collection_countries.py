# -*- coding:utf-8 -*-

from html.parser import HTMLParser
import requests
from collections import OrderedDict
import json
import time


url = 'http://www.worldometers.info/geography/how-many-countries-are-there-in-the-world/'

class CountriesHtml(HTMLParser):

    find = 0
    countries = []

    def handle_starttag(self,tag,attr):
        if tag == 'table':
            self.find = 1
        if self.find ==1 and tag == 'tr':
            self.find = 2
        if self.find == 2 and tag == 'td':
            self.find = 3
        if self.find == 3 and tag == 'a':
            self.find = 4

    def handle_endtag(self,tag):
        pass

    def handle_data(self,data):

        data = data.strip()
        if self.find == 4:
            self.countries.append(data)
            self.find = 1

    def __str__(self):
        return str(self.countries)

if __name__ == '__main__':

        r = requests.get(url)
        countries_html = CountriesHtml()
        countries_html.feed(r.content)
        print countries_html