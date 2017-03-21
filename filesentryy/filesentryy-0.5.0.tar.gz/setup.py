# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('filesentry/filesentry.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "filesentryy",
    packages = ["filesentry"],
    install_requires=[
        'colorama',
    ],
    entry_points = {
        "console_scripts": ['filesentry = filesentry.filesentry:main']
        },
    version = version,
    description = "Python command line tool to compare two directories.",
    long_description = long_descr,
    author = "Michael Rascati",
    author_email = "rascatimichael@gmail.com",
    url = "https://github.com/rascati",
    )
