#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  vim: set ts=4 sw=4 tw=79 et :
"""fbscraper setup.py"""

from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as fp:
    long_description = fp.read()

PACKAGE_NAME = "fbscraper"
__version__ = "1.0"

setup(name=PACKAGE_NAME,
      author="onyeabor",
      author_email="onyeabor@riseup.net",
      packages=["fbscraper"],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: Implementation :: CPython",
          "Topic :: Utilities"],
      description=("A cli script that scrapes images and videos from a Facebook"
                   " profile"),
      long_description=long_description,
      version=__version__,
      license="MIT",
      keywords="facebook scraper scraping",
      install_requires=["selenium==3.3.0",
                        "requests==2.13.0",
                        "pyvirtualdisplay==0.2.1"],
      )
