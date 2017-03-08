#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='takumi_config',
    version='0.1.1',
    description='Takumi service framework configuration module',
    long_description=open("README.rst").read(),
    author="Eleme Lab",
    author_email="imaralla@icloud.com",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    url='https://github.com/elemecreativelab/takumi-config',
    install_requires=[
        'PyYAML==3.12'
    ]
)
