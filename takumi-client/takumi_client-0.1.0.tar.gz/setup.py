#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast
from setuptools import setup, find_packages

# Find version
with open('takumi_client/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(
        re.search(r'__version__\s+=\s+(.*)',
                  f.read().decode('utf-8')).group(1)))

setup(
    name='takumi_client',
    version=version,
    description='Thrift client pool for Takumi',
    long_description=open("README.rst").read(),
    author="Eleme Lab",
    author_email="imaralla@icloud.com",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    url='https://github.com/elemepi/takumi-client',
    install_requires=[
        'takumi-config',
        'takumi-thrift',
        'thriftpy',
        'schema',
    ],
)
