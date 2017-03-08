#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = open('requirements.txt').read().split()

setup(
    name='Showcase',
    version='0.3',
    author='James Rutherford',
    author_email='jim@jimr.org',
    description='Like SimpleHTTPServer, only worse',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
