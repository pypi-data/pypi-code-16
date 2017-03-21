# -*- coding: utf-8 -*-
#
#   Copyright © 2017 markdown-link-style contributors.
#
#    This file is part of markdown-link-style.
#
#   markdown-link-style is free software: you can redistribute it
#   and/or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   markdown-link-style is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with markdown-link-style (see COPYING).  If not, see
#   <http://www.gnu.org/licenses/>.

"""
markdown-link-style setup.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

from markdown_link_style._version import __version__
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

config = {
    'name': 'markdown-link-style',
    'version': __version__,
    'description': 'Switch between inline and footnote link style in markdown documents.',
    'long_description': long_description,
    'platforms': 'GNU/Linux',
    'url': 'https://git.ricketyspace.net/markdown-link-style',
    'author': 'rsiddharth',
    'author_email': 's@ricketyspace.net',
    'license': 'GNU General Public License version 3 or later',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Documentation',
        'Topic :: Text Processing :: General',
        'Topic :: Utilities',
    ],
    'keywords': 'markdown link inline footnote style',
    'py_modules': ['mdl_style'],
    'packages': ['markdown_link_style'],
    'install_requires': ['mistune'],
    'entry_points': {
        'console_scripts': ['mdl-style = mdl_style:main']
    }
}

setup(**config)
