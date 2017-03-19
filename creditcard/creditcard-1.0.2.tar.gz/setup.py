# coding: UTF-8
# Copyright © 2017 Alex Forster. All rights reserved.

from setuptools import setup


setup(
    name='creditcard',
    description='A simple class for identifying, validating, and formatting credit card information (see git.io/vydSB)',
    version='1.0.2',
    author='Alex Forster',
    author_email='alex@alexforster.com',
    maintainer='Alex Forster',
    maintainer_email='alex@alexforster.com',
    url='https://github.com/alexforster/creditcard',
    packages=[
        'creditcard',
    ],
    package_dir={
        'creditcard': './creditcard',
    },
    package_data={
        'creditcard': [
            './data/registry.xml',
        ],
    }
)
