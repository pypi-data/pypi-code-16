#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from blingtron import __version__

setup(
    name='blingtron',
    version=__version__,
    description="Blingtron is a simple CLI tool aimed at helping developers run their II projects.",
    url='https://github.com/ImageIntelligence/blingtron',

    author='David Vuong',
    author_email='david@imageintelligence.com',

    classifiers=[
        'Intended Audience :: Developers',

        'Environment :: Console',

        'Topic :: Utilities',

        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    install_requires=[
        'docopt==0.6.2',
        'docker-py==1.10.6'
    ],
    include_package_data=True,
    package_data={'': ['README.md']},

    entry_points={
        'console_scripts': [
            'bling=blingtron.blingtron:main',
        ],
    },
)
