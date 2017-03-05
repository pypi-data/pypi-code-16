#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(
    name='cumtbscore',
    version='0.1.2',
    description='Student score interface for CUMTB',
    url='https://github.com/x1ah/Daily_scripts/tree/restructure/StuScore',
    author='x1ah',
    author_email='x1ahgxq@gmail.com',
    license='MIT',
    install_requires=['bs4>=0.0.1', 'prettytable>=0.7.2'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='cumtb score spider python cli',
    py_modules=['cumtbscore']
)
