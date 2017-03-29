#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='takumi_ext',
    version='0.1.1',
    description='Simple extension system for extending Takumi framework',
    long_description=open('README.rst').read(),
    author='Eleme Lab',
    author_email='imaralla@icloud.com',
    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    url='https://github.com/elemepi/takumi-ext',
    install_requires=[
        'takumi-config'
    ]
)
