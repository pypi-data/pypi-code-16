#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 juxor <ju@riseup.net>

# This file is part of afaq-dl.
#
# afaq-dl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# afaq-dl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with afaq-dl.  If not, see <http://www.gnu.org/licenses/>.
""""""

from setuptools import setup, find_packages
import afaqdl
setup(
    name='afaq-dl',
    version=afaqdl.__version__,
    description=afaqdl.__description__,
    long_description=afaqdl.__long_description__,
    author=afaqdl.__author__,
    author_email=afaqdl.__author_mail__,
    license='GPLv3+',
    url=afaqdl.__website__,

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    dependency_links=[
        "https://pypi.python.org/simple/scrapy",
        "https://pypi.python.org/simple/pyyaml",
        "https://pypi.python.org/simple/gitpython",
        "https://pypi.python.org/simple/html2text",
        "https://pypi.python.org/simple/beautifulsoup4"
    ],
    extras_require={
        'dev': ['ipython'],
        'test': ['coverage'],
    },
    #entry_points={'scrapy': ['settings = afaqdl.settings']},
    scripts=['bin/anarchism_update'],
    keywords='python scrapy afaq anarchism git html markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Environment :: Console",
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 ' +
        'or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
