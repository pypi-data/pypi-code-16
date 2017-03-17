# -*- coding:utf-8 -*-

import random
import copy
from pywse.conf.countries import questions

class Countries(object):

    def __init__(self, **kwargs):
        self.__kwargs = kwargs
        for k in kwargs:
            setattr(self, k, kwargs[k])

    @property
    def sentence(self):
        return u"{name_zh}: I'm from {name}, I am {demonym}, I speak {language}. {name} is located in {state}, the capital is {capital}."

    @property
    def ask(self):
        random_list = ['name', 'demonym']
        display_list = random.sample(random_list, 1)
        display_list.append('name_zh')
        kwargs = copy.deepcopy(self.__kwargs)
        for k in kwargs:
            if k in display_list:
                kwargs[k] = getattr(self, k)
            else:
                kwargs[k] = '____'
        return self.sentence.format(**kwargs)

    @property
    def answer(self):
        return self.sentence.format(**self.__kwargs)

class Questions(object):

    def __init__(self, country=''):
        self.ask_questions = []
        self.country = None
        for question in questions:
            if question['name'] == country or question['name_zh'] == country:
                self.country = Countries(**question)
            self.ask_questions.insert(0, Countries(**question))
        # random.shuffle(self.ask_questions)

    def start(self):
        while self.ask_questions:
            country = self.ask_questions.pop()
            raw_input(country.ask)
            print country.answer, '\n'

    def practice(self):
        if self.country:
            print self.country.answer, '\n'
        else:
            print "Can not find country, send email to haiou_chen@sina.cn for help."

def start():
    questions = Questions()
    questions.start()
