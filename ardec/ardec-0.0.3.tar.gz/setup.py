import os
import re
import sys
from setuptools import setup

NAME = "ardec"
AUTHOR = "amancevice"
EMAIL = "smallweirdnum@gmail.com"
DESC = "Parse financial strings to numbers."
LONG = """See GitHub_ for documentation.
.. _GitHub: https://github.com/amancevice/ardec"""
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Utilities",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python"]
REQUIREMENTS = ['contextlib2>=0.5.4'] if sys.version_info[0] < 3 else []


def version():
    search = r"^__version__ *= *['\"]([0-9.]+)['\"]"
    initpy = open("./ardec/__init__.py").read()
    return re.search(search, initpy, re.MULTILINE).group(1)


setup(
    name=NAME,
    version=version(),
    author=AUTHOR,
    author_email=EMAIL,
    packages=[NAME],
    url="http://www.smallweirdnumber.com",
    description=DESC,
    long_description=LONG,
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS)
