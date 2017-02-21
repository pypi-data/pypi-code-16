#!/usr/bin/env python
from setuptools import setup, find_packages

# Installation requirements needed absolutely for the program to run
install_requires = [
    'requests>=2.12.4',
]

# Additional feature sets and their requirements
extras_require = {
}

setup(
    name='mprequest',
    version='0.1',
    description='MP Requesting Library',
    author='John Hopper',
    author_email='john.hopper@jpserver.net',
    packages=find_packages(),

    install_requires=install_requires,
    extras_require=extras_require
)
