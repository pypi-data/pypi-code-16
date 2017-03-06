#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: qiulimao<qiu_limao@163.com>
# Created on 2017.03


import sys
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

from webfocus import run,extractor

install_requires = [
    'chardet>=2.2',
    'cssselect>=0.9',
    'lxml',
    'pycurl',
    'pyquery',
    'requests>=2.2',
    'click>=3.3',
    'six>=1.5.0',
]


setup(
    name='webfocus',
    version=extractor.__version__,

    description='extract the content from html docs',
    long_description=long_description,

    url='https://github.com/qiulimao',

    author='qiulimao',
    author_email='qiu_limao@163.com',

    license='Apache License, Version 2.0',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'License :: OSI Approved :: Apache Software License',

        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='html content extract',

    packages=find_packages(exclude=['data', 'tests*']),

    package_data={
        'webfocus': ['README.md'],
    },

    install_requires=install_requires,

    entry_points={
        'console_scripts': [
            'webfocus=webfocus.run:main'
        ]
    },
)
