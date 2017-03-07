#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.core import setup
from colorpicker import __author__, __version__, __license__

setup(
    name='colorpicker',
    version='1.1',
    py_modules=['colorpicker'],
    description='Color Picker Widget',
    author='tokyo-noctambulist',
    author_email='oohira-k@e-zero1.co.jp',
    url='https://github.com/tokyo-noctambulist/colorpicker',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords=['picker', 'color', 'palette'],
    license='MIT License',
    install_requires=[
        'PySide',
    ],
)
