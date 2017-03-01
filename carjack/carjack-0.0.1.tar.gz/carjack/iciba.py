# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import locale
import re
from six import text_type

import requests
from bs4 import BeautifulSoup


def encode_url(url_with_unicode):
    return requests.utils.quote(text_type(url_with_unicode).encode('utf8'))


class IcibaDict(object):
    def __init__(self, api_key=None):
        self.domain = u"http://dict-co.iciba.com/"
        self.api_key = api_key

    def search(self, query):
        if locale.getpreferredencoding(False).endswith('ASCII'):
            query = query.decode('utf8')
        if self.api_key:
            # e.g. http://dict-co.iciba.com/api/dictionary.php?key=D48AB736278DD50AE428D43E2FF9B08C&type=json&w=扯淡
            params = {'key': self.api_key, 'type': 'json', 'w': query}
            url = self.domain + u"api/dictionary.php?".format(self.api_key, query)
        else:
            # e.g. http://dict-co.iciba.com/search.php?word=%E6%9E%9C&submit=%E6%9F%A5%E8%AF%A2
            params = {'submit': '%E6%9F%A5%E8%AF%A2', # i.e. u'查询'
                      'word': query}
            url = self.domain + u"search.php?".format(query)
        response = requests.get(url, params=params)
        return response

    def parse_json(self, json_response):
        json_object = json.loads(json_response.content.decode('utf8'))
        return json_object

    def print_json(self, json_object):
        print(json.dumps(json_object, indent=4))

    def extract_meaning_from_json(self, json_response):
        json_object = self.parse_json(json_response)
        for meaning in json_object['symbols'][0]['parts'][0]['means']:
            yield meaning['word_mean']

    def extract_meaning_from_html(self, html_response):
        soup = BeautifulSoup(html_response.content.decode('utf8'),  "html5lib")
        meanings = re.sub(u'返回查词首页$', '', soup.find('body').text.strip()).strip()
        return meanings.split('\xa0\xa0')
