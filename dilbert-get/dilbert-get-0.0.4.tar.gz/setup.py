# -*- coding: utf-8 -*-
#
# This file is part of the dilbert-get project
#
# Copyright (c) 2017 Tiago Coutinho
# Distributed under the MIT license. See LICENSE for more info.

import os
import sys
from setuptools import setup

requirements = [
    'grequests',
    'bs4',
]

setup(
    name='dilbert-get',
    version='0.0.4',
    description="downloader of dilbert comics",
    author="Tiago Coutinho",
    author_email='coutinhotiago@gmail.com',
    url='https://github.com/tiagocoutinho/dilbert',
    py_modules=['dilbert_get'],
    entry_points={
        'console_scripts': [
            'dilbert-get=dilbert_get:main'
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    keywords='dilbert',
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
