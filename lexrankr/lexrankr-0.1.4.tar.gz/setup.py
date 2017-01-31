#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test


requirements = [
    'setuptools',
    'networkx',
    'konlpy',
    'scipy',
    'numpy',
    'gensim',
    'sklearn',
    'MCL_Markov_Cluster',
]
if sys.version_info < (3, ):
    requirements.append('jpype1')
else:
    requirements.append('jpype1-py3')

setup(
    name='lexrankr',
    version='0.1.4',
    license='MIT',
    author='Jamie Seol',
    author_email='theeluwin@gmail.com',
    url='https://github.com/theeluwin/lexrankr',
    description='LexRank for Korean',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[],
)
