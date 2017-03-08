#!/usr/bin/env python

"""Setup script for the 'pyonlinedict' distribution."""

from distutils.core import setup, Extension
from setuptools import setup,find_packages

setup (name = "pyonlinedict",
       version = "1.0.6",
       description = "Python online command-line dictionary",
       url = "https://github.com/sunnyelf/pyonlinedict",
       author = "sunnyelf",
       long_description = "Python online command-line dictionary",
       keywords = ("Python,online,command-line,dictionary"),
       license = "GPL V3 License",
       author_email = "q_a_q@outlook.org",
       packages = find_packages(),
       scripts = ['scripts/pyonlinedict.py'],
       platforms = "linux"
      )
