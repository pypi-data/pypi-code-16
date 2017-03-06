#!/usr/bin/env python
# coding=utf-8
"""
Setup.py for Mal-py
"""

from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_dsecription = f.read()

config = {
    'url': 'https://github.com/LSmit202/Mal-Py',
    'name': 'malpy',
    'version': '0.5.0',
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
    'packages': ['malpy'],
    'install_requires': [],
    'tests_require': [
        'nose'
    ],
    'extras_require': {
        'test': [
            'nose'
        ],
        'docstest': [
            'doc8',
            'pyenchant',
            'readme_renderer >= 16.0',
            'sphinx',
            'sphinx_rtd_theme',
            'sphinxcontrib-spelling'
        ],
        'pep8test': [
            'flake8',
            'flake8-import-order',
            'pep8-naming'
        ]
    }
}

setup(**config)
