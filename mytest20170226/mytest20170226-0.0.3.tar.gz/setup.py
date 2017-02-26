#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version='0.0.3'

requirements = [line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "requirements.txt"))]

setup(
    name='mytest20170226',
    version=version,
    description='mytest',
    # long_description=readme,
    packages=['mytest20170226'],
    install_requires=requirements,
    include_package_data=True,
    url="https://www.mytest.com",
    classifiers=[
	    'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
