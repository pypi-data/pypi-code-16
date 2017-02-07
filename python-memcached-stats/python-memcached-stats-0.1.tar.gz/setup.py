#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='python-memcached-stats',
    version='0.1',
    description='Python class to gather stats and slab keys from memcached via the memcached telnet interface',
    author='Abhishek Shrivastava',
    author_email='abhishek.shrivastava.ts@gmail.com',
    url='http://github.com/abstatic/python-memcached-stats',
    package_dir={'': 'src'},
    py_modules=[
        'memcached_stats',
    ],
)
