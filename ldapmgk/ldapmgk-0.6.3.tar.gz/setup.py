#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Packaging settings"""

import io
from ldapmgk import __version__
from os.path import abspath, dirname, join

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

this_dir = abspath(dirname(__file__))
with io.open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

config = {
    'name': 'ldapmgk',
    'version': __version__,
    'description': 'Helper for managing an LDAP directory on CLI',
    'long_description': long_description,
    'url': 'https://github.com/Movile/ldapmgk',
    'author': 'Hugo Cisneiros',
    'author_email': 'hugo.cisneiros@movile.com',
    'license': 'GPLv3',
    'classifiers': [
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    'keywords': [
        'ldap',
        'manager'
    ],
    'packages': find_packages(exclude=['docs', 'tests*']),
    'install_requires': ['docopt', 'python-ldap', 'Jinja2'],
    'extras_require': {
        'test': ['nose'],
    },
    'entry_points': {
        'console_scripts': [
            'ldapmgk=ldapmgk.cli:main',
        ],
    },
}

setup(**config)
