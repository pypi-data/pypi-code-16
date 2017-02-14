#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='colortable',
    py_modules=['colortable'],  # this must be the same as the name above
    version='0.2',
    description='Print colorful(256) tables for terminal with built-in themes',
    author='lethe3000',
    author_email='lethe30003000@gmail.com',
    url='https://github.com/lethe3000/ctable',  # use the URL to the github repo
    download_url='https://github.com/lethe3000/ctable/tarball/0.1',  # I'll explain this in a second
    keywords=['table', 'terminal', 'print'],  # arbitrary keywords
    classifiers=[],
    install_requires=['tabulate==0.7.7'],
)
