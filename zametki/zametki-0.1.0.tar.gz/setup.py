#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of zametki.
# https://github.com/Mechasparrow/zametki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2017, Michael Navazhylau <mikipux7@gmail.com>

from setuptools import setup, find_packages
from zametki import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='zametki',
    version=__version__,
    description='A python package for writing logs',
    long_description='''
A python package for writing logs
''',
    keywords='brain mind search',
    author='Michael Navazhylau',
    author_email='mikipux7@gmail.com',
    url='https://github.com/Mechasparrow/zametki',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # add your dependencies here
        # remember to use 'package-name>=x.y.z,<x.y+1.0' notation (this way you get bugfixes)
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            'zametki=zametki.cli:main',
        ],
    },
)
