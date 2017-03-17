#!/usr/bin/env python
from setuptools import setup, find_packages
import os

setup(
      name="python-instagram-fixed",
      version="1.0.1",
      description="Life extended Instagram API client",
      license="MIT",
      install_requires=["simplejson", "httplib2", "six"],
      author="Orcun Gumus",
      author_email="gumus@somed.io",
      url="https://github.com/guemues/python-instagram-fixed",
      packages = find_packages(),
      keywords= "instagram"
)
