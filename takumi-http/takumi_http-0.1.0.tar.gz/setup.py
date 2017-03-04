#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='takumi_http',
    version='0.1.0',
    description='Http to thrift protocol conversion',
    long_description=open("README.rst").read(),
    author="Eleme Lab",
    author_email="imaralla@icloud.com",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    url='https://github.com/elemepi/takumi-http',
    install_requires=[
        'takumi-thrift',
        'takumi-service',
        'thriftpy',
    ],
)
