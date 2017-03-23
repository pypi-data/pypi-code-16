#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup, find_packages
setup(
    name="lazyiter",
    description='Easy lazy iteration (generation) over a database table',
    version="0.1",
    packages=find_packages(),
    author='Sam Zhang',
    url='https://github.com/samzhang111/lazyiter',
    install_requires=['sqlalchemy', 'psycopg2']
)
