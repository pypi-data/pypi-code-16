#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

try:
    from .packages.crawlib import exc
    from .packages.crawlib.htmlparser import BaseHtmlParser
except:
    from crawl_zillow.packages.crawlib import exc
    from crawl_zillow.packages.crawlib.htmlparser import BaseHtmlParser


class HTMLParser(BaseHtmlParser):
    def get_all_state(self, html):
        soup = self.get_soup(html)
        all_state = list()
        
        div = soup.find("div", id="region-content")
        for ul in div.find_all("ul", class_="items-list"):
            for a in ul.find_all("a"):
                state_href = a["href"]
                state_abbr = state_href.split("/")[-1]
                state_name = a.text
                all_state.append({"state_href": state_href,
                                  "state_abbr": state_abbr,
                                  "state_name": state_name,})
        return all_state
    
    def get_all_city(self, html):
        soup = self.get_soup(html)
        all_city = list()
        
        div = soup.find("div", id="region-content")
        for ul in div.find_all("ul", class_="items-list"):
            for a in ul.find_all("a"):
                city_href = a["href"]
                city_code = city_href.split("/")[-3]
                city_name = a.text
                all_city.append({"city_href": city_href,
                                  "city_code": city_code,
                                  "city_name": city_name,})
        return all_city


htmlparser = HTMLParser()


if __name__ == "__main__":
    from os.path import join, exists
    from pprint import pprint as ppt
    
    from pathlib_mate import Path
    
    from crawl_redfin.urlencoder import urlencoder
    from crawl_redfin.pkg.dataIO.textfile import read, write
    
    import time
    from selenium_spider import ChromeSpider
    
    executable_path = r"C:\Users\shu\Documents\PythonWorkSpace\py3\py33_projects\crawl_redfin-project\chromedriver.exe"
    driver = ChromeSpider(executable_path)
    
    with driver as spider:
        def get_path(filename):
            return join("testhtml", filename)
        
        def test_get_all_state():
            url = urlencoder.state_listpage()
            path = get_path("all_state.html")
            if not exists(path):
                html = spider.get_html(url)
                write(html, path)
            
            html = read(path)
            ppt(htmlparser.get_all_state(html))
            
        test_get_all_state()
    
        def test_get_all_city():
            for state_abbr in [
                    "MD", 
                    "VA",
                ]:
                url = urlencoder.city_listpage("states/%s" % state_abbr, "A")
                path = get_path("state_%s.html" % state_abbr)
                if not exists(path):
                    html = spider.get_html(url)
                    write(html, path)
            
                html = read(path)
                ppt(htmlparser.get_all_city(html))
            
        test_get_all_city()