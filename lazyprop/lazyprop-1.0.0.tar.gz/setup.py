#!/usr/bin/env python

from setuptools import setup
from lazyprop import __version__


setup(
    name='lazyprop',
    version=__version__,
    description='Decorator to make class properties load lazily and cache',
    author='Bryan Johnson',
    author_email='d.bryan.johnson@gmail.com',
    packages=['lazyprop'],
    url='https://github.com/dbjohnson/lazyprop',
    download_url='https://github.com/dbjohnson/lazyprop/tarball/%s' % __version__
)
