#!/usr/bin/env python

from distutils.core import setup

setup(
    name='consul-locator',
    version='0.1.6',
    description='python consul discovery locator for http',
    author='Thinh Tran',
    author_email='duythinht@gmail.com',
    url='http://git.chotot.org/thinhtran/python-consul-locator',
    py_modules=['locator'],
    install_requires=['requests', 'python-consul'],
)
