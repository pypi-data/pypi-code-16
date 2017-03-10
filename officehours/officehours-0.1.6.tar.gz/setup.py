#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = '0.1.6'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    os.system('git tag -a {0} -m "v{0}"'.format(__version__))
    os.system('git push --tags')
    sys.exit()


setup(
    name = 'officehours',
    packages = ['officehours'],
    version = '0.1.6',
    description = 'Utility to calculate time intervals in working hours',
    author = 'Guillermo Guirao Aguilar',
    author_email = 'contact@guillermoguiraoaguilar.com',
    url = 'https://github.com/Funk66/officehours.git',
    keywords = ['time', 'hours', 'office', 'business', 'work'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ]
)
