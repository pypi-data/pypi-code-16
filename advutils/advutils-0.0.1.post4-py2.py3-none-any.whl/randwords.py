# -*- coding: utf-8 -*-
"""
This module have some utilities to create random words from source

Created on Thu Jan 28 16:59:13 2016

@author: dev
"""
from __future__ import print_function
# http://stackoverflow.com/a/18835426
from future import standard_library
standard_library.install_aliases()
from builtins import map
from builtins import range
import urllib.request
import urllib.error
import urllib.parse
import random
import string


def getwords(var):
    """
    Get whole words from string that are formed with ascii letters.

    :param var:
    :return:
    """
    words = set()
    word = ""
    letters = string.ascii_letters + "".join(map(str, list(range(10))))
    for l in var:
        if l in letters:
            word += l
        else:
            words.add(word)
            word = ""
    return list(words)  # urllib2.urlopen(word_site).read().splitlines()


def sitewords(word_site=None):
    """
    Get words from web.

    :param word_site:
    :return:
    """
    if word_site is None:
        word_site = "http://www.freebsd.org/cgi/cvsweb.cgi/src/share/dict/web2?rev=1.12;content-type=text%2Fplain"
    return getwords(urllib.request.urlopen(word_site).read())


def filewords(path=None):
    """
    Get words from file.

    :param path:
    :return:
    """
    if path is None:
        path = __file__
    with open(path, "r") as f:
        return getwords(f.read())


try:
    base_source = sitewords()
except:
    base_source = filewords()


def generate(source=None, minwords=2, maxwords=5, rand=True):
    """
    Generate random words from source

    :param source:
    :param minwords:
    :param maxwords:
    :param rand:
    :return:
    """
    if source is None:
        source = base_source  # use global source

    def pickword():
        return source[int(random.random() * (len(source) - 1))]

    def numwords():
        if rand:
            return int(minwords + random.random() * (maxwords - minwords))
        else:
            return maxwords
    return [pickword() for _ in range(numwords())]


if __name__ == "__main__":
    print(base_source)
