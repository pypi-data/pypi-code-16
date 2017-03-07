# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "synq"
VERSION = "1.0.0"



# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["requests"]

setup(
    name=NAME,
    version=VERSION,
    description="SYNQ Video API",
    author="synq",
    author_email="sales@synq.fm",
    url="https://synq.fm",
    license='MIT',
    keywords=["SYNQ Video API"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    long_description="""\
    The SYNQ video API
    """,
    test_suite="tests"
)


