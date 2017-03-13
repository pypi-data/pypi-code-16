#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import takumi_http


setup(
    name='takumi_http',
    version=takumi_http.__version__,
    description='Http to thrift protocol conversion',
    long_description=open("README.rst").read(),
    author="Eleme Lab",
    author_email="imaralla@icloud.com",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    url='https://github.com/elemepi/takumi-http',
    install_requires=[
        'takumi',
        'takumi-thrift',
        'thriftpy',
    ],
)
