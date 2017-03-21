#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
from pkgutil import walk_packages
from setuptools import setup


def find_packages(path):
    return [name for _, name, is_pkg in walk_packages([path]) if is_pkg]


def read_file(filename):
    with io.open(filename) as fp:
        return fp.read().strip()


setup(
    name='avc-scrapy-helper',
    version='0.0.3',
    description="scrapy helper for scrapy.",
    author="openedbox",
    author_email='openedbox@qq.com',
    url='https://github.com/openedbox/avc-scrapy-helper',
    packages=list(find_packages('src')),
    package_dir={'': 'src'},
    license="MIT"
)

