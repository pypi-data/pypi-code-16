# -*- coding: utf-8 -*-
import pprint

from colorama import Fore
from colorama import Style


class Printer(object):
    def __init__(self, level):
        self.__level = level

    def up(self):
        self.__level += 1

    def down(self):
        self.__level -= 1

    def show(self, text):
        print(' ' * 2 * self.__level + text)


def blue(*texts):
    return __wrapper_with(Fore.BLUE, Fore.RESET, texts)


def green(*texts):
    return __wrapper_with(Fore.GREEN, Fore.RESET, texts)


def red(*texts):
    return __wrapper_with(Fore.RED, Fore.RESET, texts)


def bold(*texts):
    return __wrapper_with(Style.BRIGHT, Style.NORMAL, texts)


def dump(o):
    return pprint.pformat(o)


def __wrapper_with(before, after, texts):
    return ''.join([before + str(text) + after for text in texts])


printer = Printer(0)
