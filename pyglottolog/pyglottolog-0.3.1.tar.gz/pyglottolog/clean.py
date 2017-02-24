# coding: utf8
from __future__ import unicode_literals, print_function, division
import os
from glob import glob
import io
from csv import writer


def read(fp):
    res = []
    for line in fp:
        cols = line.split(',')
        res.append(cols)
    return res


def walk(d):
    for fname in os.path.join(d, '*.csv'):
        data = read(fname)
