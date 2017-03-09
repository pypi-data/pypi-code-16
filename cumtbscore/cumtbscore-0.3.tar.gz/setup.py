#!/usr/bin/env python
# encoding: utf-8

from distutils.core import setup
from setuptools import find_packages

setup(
    name='cumtbscore',
    version='0.3',
    description='Student score interface for CUMTB',
    url='https://github.com/x1ah/Daily_scripts/tree/restructure/StuScore',
    author='x1ah',
    author_email='x1ahgxq@gmail.com',
    license='MIT',
    install_requires=['bs4', 'prettytable'],
    classifiers=[],
    keywords='cumtb score spider python cli',
    packages = ['cumtbscore']
)

