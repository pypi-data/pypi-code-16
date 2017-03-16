#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='aspic',
    version='2017.3.16.1',
    description='Asyncio and Qt versions of SpecClient for Python 3',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/aspic',
    license='GPLv3',
    package_dir={'aspic': ''},
    py_modules=[
        'aspic.__init__',
        'aspic.connection',
        'aspic.const',
        'aspic.excepts',
        'aspic.header',
        'aspic.manager',
        'aspic.message',
        'aspic.motor',
        'aspic.qommand',
        'aspic.qmotor',
        'aspic.qonnection',
        'aspic.qounter',
        'aspic.reply',
    ],
)
