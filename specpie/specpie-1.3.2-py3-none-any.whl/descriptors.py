# -*- coding: utf-8 -*-
from specpie.printer import printer, bold, blue


class Descriptor(object):

    def __init__(self, message):
        self.__message = message

    def __enter__(self):
        printer.show(self.__message)
        printer.up()

    def __exit__(self, exc_type, exc_val, exc_tb):
        printer.down()
        return exc_type == AssertionError


def describe(text: str) -> Descriptor:
    """
    Create a describe statement with the given text
    :type text: str
    :rtype: None
    """
    return Descriptor(blue(bold('Describe: ')) + text)


def context(text: str) -> Descriptor:
    """
    Create a context statement with the given text
    :type text: str
    :rtype: None
    """
    return Descriptor(blue(bold('Context: ')) + text)


def it(text: str) -> Descriptor:
    """
    Create a it statement with the given text
    :type text: str
    :rtype: None
    """
    return Descriptor(blue(bold('It: ')) + text)


