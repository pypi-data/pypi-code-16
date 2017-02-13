#!/usr/bin/env python

from setuptools import setup

setup(name="LoProp",
    version="0.2.2",
    packages=["loprop"],
    scripts=['scripts/loprop'],
    author="Olav Vahtras",
    author_email="vahtras@kth.se",
    install_requires = ["daltools"],
    description = 'LoProp implementation for Dalton',
    )
