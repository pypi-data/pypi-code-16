# -*- coding:utf-8 -*-

from html.parser import HTMLParser
import requests
from collections import OrderedDict
import json
import time
from pywse.conf.countries import countries_list
import traceback

countries = countries_list
url = 'https://en.wikipedia.org/wiki/%s'


DEBUG = False

class CountriesHtml(HTMLParser):

    def __init__(self, country):
        self.conditions = {
            'capital': {
                'condition': [
                    {'<data>': 'Capital'},
                    {'tag': 'a'},
                    {'tag': 'td'},
                    {'tag': 'table'},
                ],
                'value': '',
                'value_index': 2,
            },
            'demonym': {
                'condition': [
                    {'<data>': 'Demonym'},
                    {'tag': 'a'},
                    {'tag': 'td'},
                    {'tag': 'table'},
                ],
                'value': '',
                'value_index': 2,
            },
            'language': {
                'condition': [
                    {'<data>': 'languages'},
                    {'tag': 'a'},
                    {'tag': 'td'},
                    {'tag': 'table'},
                ],
                'value': '',
                'value_index': 2,
            },
            'currency': {
                'condition': [
                    {'<data>': 'Currency'},
                    {'tag': 'a'},
                    {'tag': 'td'},
                    {'tag': 'table'},
                ],
                'value': '',
                'value_index': 2,
            },
        }
        self.country = country
        self.find_capital = 0
        self.kwargs = { 'state': '', 'name': country }
        self.states = ['North America', 'South America', 'Asia', 'Africa', 'Europe', 'Oceania']
        HTMLParser.__init__(self)

    def pop_condition(self, arg):
        if not arg in self.conditions:
            return
        condition = self.conditions[arg]['condition']
        last_dict = condition.pop()
        if '<data>' in last_dict:
            self.kwargs[arg] = self.conditions.pop(arg)['value_index']

    def handle_starttag(self,tag,attr):
        for arg in self.conditions.keys():
            condition = self.conditions[arg]['condition'][-1]
            if 'tag' in condition:
                self.pop_condition(arg=arg)

    def handle_endtag(self,tag):
        pass

    def set_state(self, data):
        if self.kwargs['state'] is '':
            for state in self.states:
                if state in data:
                    self.kwargs['state'] = state

    def handle_data(self,data):

        data = data.strip()
        if data:
            self.set_state(data=data)

        for arg in self.kwargs:
            if isinstance(self.kwargs[arg], int):
                self.kwargs[arg] -= 1
                if DEBUG is True:
                    print arg, data.decode('utf=8'), self.kwargs[arg]
                if self.kwargs[arg] is 0:
                    if data in ('and largest city', '','Largest city'):
                        self.kwargs[arg] += 1
                    else:
                        if isinstance(data, unicode):
                            self.kwargs[arg] = data
                        else:
                            self.kwargs[arg] = data.decode('utf-8')

        for arg in self.conditions.keys():
            condition = self.conditions[arg]['condition'][-1]
            if '<data>' in condition:
                if data == condition['<data>']:
                    self.kwargs[arg] = None
                    self.pop_condition(arg=arg)

    @property
    def infos(self):
        result = OrderedDict()
        for arg in ('name', 'state', 'demonym', 'language', 'currency', 'capital'):
            result[arg] = '{%s}' % (arg)
            if not arg in self.kwargs:
                self.kwargs[arg] = ''
        result = json.dumps(result)
        result = result[1:-1]
        result = unicode(result)
        result = result.format(**self.kwargs)
        result = '    {' + result + '}'
        return result.encode('utf-8')

if __name__ == '__main__':

    for country in countries:
        while True:
            try:
                c_url = url % (country)
                r = requests.get(c_url)
                countries_html = CountriesHtml(country=country)
                countries_html.feed(r.content.decode('utf-8'))
                f_countries = open('countries.txt', 'a+')
                print countries_html.infos
                f_countries.write(countries_html.infos + '\n')
                f_countries.close()
                del countries_html
                time.sleep(1)
                break
            except:
                f_error = open('error.txt', 'a+')
                f_error.write(country + ':\n')
                f_error.write(traceback.format_exc())
                f_error.close()
