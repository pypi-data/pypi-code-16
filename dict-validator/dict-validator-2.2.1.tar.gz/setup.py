#!/usr/bin/python
import os

from setuptools import setup, find_packages

SRC_DIR = os.path.dirname(__file__)
CHANGES_FILE = os.path.join(SRC_DIR, "CHANGES")

with open(CHANGES_FILE) as fil:
    version = fil.readline().split()[0]


setup(
    url="https://github.com/gurunars/dict-validator",
    name="dict-validator",
    install_requires=[],
    description="A library for structural data validation.",
    version=version,
    packages=find_packages(exclude=["test"]),
    author="Anton Berezin",
    author_email="gurunars@gmail.com",
    include_package_data=True
)
