#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Antoine Bertin <diaoulael@gmail.com>
# Copyright (c) 2017 Martin Bachmann <bachmmar@gmail.com>
#
# This file is part of pyjulius3.
#
# pyjulius is free software; you can redistribute it and/or modify it under
# the terms of the Lesser GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# pyjulius is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU Lesser General Public License for more details.
#
# You should have received a copy of the Lesser GNU Lesser General Public License
# along with pyjulius3.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup
exec(compile(open('pyjulius3/infos.py').read(), 'pyjulius3/infos.py', 'exec'))

setup(name='pyjulius3',
    version=__version__,
    license='LGPLv3',
    description='Simple interface to connect to a julius module server',
    long_description=open('README.rst').read() + '\n\n' +
                     open('NEWS.rst').read(),
    classifiers=['Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    keywords='julius speech recognition',
    author='Martin Bachmann',
    author_email='bachmmar@gmail.com',
    url='https://github.com/bachmmmar/pyjulius',
    packages=['pyjulius3'])
