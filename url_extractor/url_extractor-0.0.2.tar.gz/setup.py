#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: dennis
# Mail: xfl1991@gmail.com
# Created Time:  2016-12-25 01:25:34 AM
#############################################


from setuptools import setup, find_packages

setup(
    name = "url_extractor",
    version = "0.0.2",
    keywords = ("pip", "url_extractor", "dennis"),
    description = "extract the domain from a url",
    long_description = "extract the domain from a url in python",
    license = "MIT Licence",

    url = "http://mikolaje.github.io",
    author = "dennis",
    author_email = "xfl1991@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
