#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import (
    setup
)

from thumbor_head import __version__

setup(
    name = "thumbor_head",
    packages = ["thumbor_head"],
    version = __version__,
    description = "Allow checking of http status code for all requests even if cached",
    author = "Eric hermelin",
    author_email = "eric.hermelin@gmail.com",
    keywords = ["thumbor",  "images", 'plugin'],
    package_dir = {"thumbor_head": "thumbor_head"},
    install_requires=["thumbor>=3.3.0"],
    url='https://github.com/torsdag/thumbor_head',  # use the URL to the github repo
    long_description = """\
Thumbor is a smart imaging service. It enables on-demand crop, resizing and flipping of images.
This module always sends a head request to the server to make sure the file is still
available and the user still has permission to access it.
"""
)