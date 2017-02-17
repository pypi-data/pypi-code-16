#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='daveluo_utils',
    version='0.1',
    keywords=('daveluo', 'utils'),
    description='一些开发常用的工具',
    license='Free',
    author='Dave Luo',
    author_email='kitsudo163@163.com',
    url='http://www.baidu.com',
    platforms='any',
    packages=find_packages(exclude=['data', 'tests*']),
    package_dir={
        "utils": "utils",
    }
)
