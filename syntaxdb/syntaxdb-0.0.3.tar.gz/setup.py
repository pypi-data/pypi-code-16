#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "syntaxdb",
    version = "0.0.3",
    author = "lhat-messorem",
    author_email = "lhat.messorem@gmail.com",
    description = ("A small Python library for accessing the SyntaxDB API"),
    license = "MIT",
    keywords = "syntaxdb",
    url = "https://github.com/lhat-messorem/syntax_db",
    packages=['syntaxdb'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    package_data={
        "": ["README.md", "LICENSE.md"]
    }
)