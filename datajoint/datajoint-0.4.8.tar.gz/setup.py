#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

long_description = "An object-relational mapping and relational algebra to facilitate data definition and data manipulation in MySQL databases."

# read in version number
with open(path.join(here, 'datajoint', 'version.py')) as f:
    exec(f.read())

setup(
    name='datajoint',
    version=__version__,
    description="An ORM with closed relational algebra",
    long_description=long_description,
    author='Dimitri Yatsenko',
    author_email='Dimitri.Yatsenko@gmail.com',
    license="GNU LGPL",
    url='https://github.com/datajoint/datajoint-python',
    keywords='database organization',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['numpy', 'pyparsing', 'networkx', 'matplotlib', 'pymysql>=0.7.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
