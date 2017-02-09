#!/usr/bin/env python3

"""NCC Performance Analyser API to ElasticSearch coupler"""

import os
from setuptools import setup
from pip.req import parse_requirements

reqs_path = os.path.dirname(os.path.realpath(__file__)) + '/requirements/release.txt'
install_reqs = parse_requirements(reqs_path, session=False)
requires = [str(ir.req) for ir in install_reqs]

setup(
    name='ncc_paapi',
    version='0.0.1',
    description='Abstraction classes to access the PA API',
    author='NCC Group',
    packages=['paapi'],
    install_requires=requires,
    url='https://github.com/ncc-tools/python-pa-api'
)
