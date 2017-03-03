#!/usr/bin/env python
# coding=utf-8
"""
Setup.py for Mal-py
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_dsecription = f.read()

config = {
    'url': 'https://github.com/LSmit202/malpy',
    'name': 'malpy',
    'version': '0.3.2',
    'description': 'Minimal Assembly Language Virtual Machine',
    'long_description': long_dsecription,
    'author': 'Luke Smith',
    'author_email': 'lsmit202@musdenver.edu',
    'license': 'BSD',
    'entry_points': {
        'console_scripts': [
            'malpy = malpy.__main__:main'
        ]
    },
    'packages': find_packages()
}

setup(**config)
