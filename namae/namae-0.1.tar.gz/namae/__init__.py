# -*- coding:utf-8 -*-
import keyword
import re
from functools import partial


def normalize(name, ignore_rx=re.compile("[^0-9a-zA-Z_]+")):
    c = name[0]
    if c.isdigit():
        name = "n" + name
    elif not (c.isalpha() or c == "_"):
        name = "x" + name
    elif keyword.iskeyword(name):
        name = name + "_"
    return ignore_rx.sub("", name.replace("-", "_"))


def titleize(name):
    if not name:
        return name
    name = str(name)
    return "{}{}".format(name[0].upper(), name[1:])


def untitleize(name):
    if not name:
        return name
    return "{}{}".format(name[0].lower(), name[1:])


def snakecase(name, rx0=re.compile('(.)([A-Z][a-z]+)'), rx1=re.compile('([a-z0-9])([A-Z])'), separator="_"):
    pattern = r'\1{}\2'.format(separator)
    return rx1.sub(pattern, rx0.sub(pattern, name)).lower()


kebabcase = lispcase = partial(snakecase, separator="-")


def camelcase(name):
    return untitleize(pascalcase(name))


def pascalcase(name, rx=re.compile("[\-_ ]")):
    return "".join(titleize(x) for x in rx.split(name))
