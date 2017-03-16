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
        return "I am {demonym}, I'm from {name}, I speak {language}. {name} is located in {state}, the capital is {capital}."

    @property
    def ask(self):
        random_list = ['name', 'demonym']
        display_list = random.sample(random_list, 1)
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

    def __init__(self):
        self.ask_questions = []
        for question in questions:
            self.ask_questions.insert(0, Countries(**question))
        random.shuffle(self.ask_questions)

    def start(self):
        while self.ask_questions:
            country = self.ask_questions.pop()
            raw_input(country.ask)
            print country.answer, '\n'

def start():
    questions = Questions()
    questions.start()
