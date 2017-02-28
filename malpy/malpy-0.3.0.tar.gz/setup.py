#!/usr/bin/env python
# coding=utf-8
"""
Setup.py for Mal-py
"""


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_dsecription = f.read()

config = {
    'url': 'https://github.com/LSmit202/mal',
    'name': 'malpy',
    'version': '0.3.0',
    'description': 'Minimal Assembly Language Virtual Machine',
    'long_description': long_dsecription,
    'author': 'Luke Smith',
    'author_email': 'lsmit202@musdenver.edu',
    'license': 'BSD',
    'entry_points': {
        'console_scripts': [
            'mal = mal.__main__:main'
        ]
    },
    'packages': ['mal']
}

setup(**config)
