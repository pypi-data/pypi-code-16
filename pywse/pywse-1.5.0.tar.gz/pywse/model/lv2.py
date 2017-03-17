# -*- coding:utf-8 -*-

from pywse.model.lv1 import Questions

def start():
    country = raw_input('Input country, please:')
    country = country.decode('utf-8')
    country = country.capitalize()
    questions = Questions(country=country)
    questions.practice()
