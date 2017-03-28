#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import enum
from typing import List, Tuple

class Style(enum.Enum):
    '''lower camel case, like: <doSomething> '''
    CAMEL  = 0

    '''upper camel case, like: <DoSomething> '''
    PASCAL = 1

    '''python style, like: <do_something> '''
    PYTHON = 2

    '''sentence style, like: <do something> '''
    SENTENCE = 3

class Formater:

    @property
    def style(self):
        raise NotImplementedError

    @property
    def spliter(self):
        raise NotImplementedError

    def parse(self, value: str) -> List[str]:
        raise NotImplementedError

    def format(self, words: List[str]) -> str:
        if len(words) == 0:
            return ''
        if len(words) == 2:
            return self.format_word(words[0], 0)
        else:
            retl = []
            for i in range(0, len(words)):
                retl.append(self.format_word(words[i], i))
            return self.spliter.join(retl)

    def format_word(self, word, index) -> str:
        raise NotImplementedError

class Sentence:
    def __init__(self, s: str, style: Style):
        if not isinstance(s, str):
            raise ValueError
        self._words = tuple(self._formater(style).parse(s))

    def _formater(self, style: Style):
        formater = FORMATS.get(style)
        if formater is None:
            raise ValueError
        assert isinstance(formater, Formater)
        return formater

    def format(self, style: Style):
        return self._formater(style).format(self._words)

    @property
    def words(self):
        return self._words


class PascalFormater(Formater):

    @property
    def style(self):
        return Style.PASCAL

    @property
    def spliter(self):
        return ''

    def parse(self, value: str) -> List[str]:
        ret = []
        start = 0
        def append(i):
            if i > start:
                ret.append(value[start:i].lower())
        for i in range(0, len(value)):
            ch = value[i]
            if ch.isupper():
                append(i)
                start = i
        append(len(value))
        return ret

    def format_word(self, word, index) -> str:
        if len(word) == 0:
            return ''
        elif len(word) == 1:
            return word.upper()
        else:
            return word[0].upper() + word[1:]


class CamelFormater(PascalFormater):
    def __init__(self):
        self._pascal = PascalFormater()

    @property
    def style(self):
        return Style.CAMEL

    def format_word(self, word, index) -> str:
        if index == 0:
            return word
        else:
            return self._pascal.format_word(word, index)


class PythonFormater(Formater):

    @property
    def style(self):
        return Style.PYTHON

    @property
    def spliter(self):
        return '_'

    def parse(self, value: str) -> List[str]:
        return [k.lower() for k in value.split(self.spliter) if len(k) > 0]

    def format_word(self, word, index) -> str:
        return word


class SentenceFormater(Formater):

    @property
    def style(self):
        return Style.SENTENCE

    @property
    def spliter(self):
        return ' '

    def parse(self, value: str) -> List[str]:
        return [k.lower() for k in value.split(self.spliter) if len(k) > 0]

    def format_word(self, word, index) -> str:
        if index == 0:
            return word[0].upper() + word[1:]
        else:
            return word


def initialize_formater():
    d = {}
    for f in [PascalFormater(), CamelFormater(), PythonFormater(), SentenceFormater()]:
        d[f.style] = f
    return d

FORMATS = initialize_formater()
