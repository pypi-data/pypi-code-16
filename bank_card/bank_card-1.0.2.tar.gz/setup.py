#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: contactxjw@gmail.com
# Created at 2016-12-08

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as fp:
    README = fp.read()

setup(
    name='bank_card',
    version='1.0.2',
    keywords=['bank card', 'python'],
    description='Get bank card info according to bank card number!',
    long_description=README,
    author='xjw0914',
    author_email='contactxjw@gmail.com',
    classifiers=[
        'Programming Language :: Python',
    ],
    license='apache-2.0',
    url='https://github.com/xjw0914/bank-card',
    download_url='https://github.com/xjw0914/bank-card',
    packages=['bank_card'],
    test_suite="tests",
)
