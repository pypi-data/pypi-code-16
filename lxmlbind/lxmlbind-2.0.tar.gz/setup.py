#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from lxmlbind import __version__

__build__ = ""

readme = open("README.md").read()

setup(
    name="lxmlbind",
    version=__version__ + __build__,
    description="Python LXML object binding.",
    long_description=readme,
    author="Jesse Myers",
    author_email="jesse@devnull.com",
    url="https://github.com/jessemyers/lxmlbind",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=["*.tests"]),
    install_requires=[
        "lxml>=3.2.4",
        "six>=1.10",
    ],
    tests_require=[
        "nose>=1.3.0",
    ],
    test_suite="lxmlbind.tests",
    include_package_data=True,
)
