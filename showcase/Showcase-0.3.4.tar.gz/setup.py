#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = open('requirements.txt').read().split()

setup(
    name='Showcase',
    version='0.3.4',
    author='James Rutherford',
    author_email='jim@jimr.org',
    description='Like SimpleHTTPServer, only worse',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    test_suite='tests',
    classifiers=[
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'Topic :: Utilities',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 2',
	'Programming Language :: Python :: 3',
    ],
)
