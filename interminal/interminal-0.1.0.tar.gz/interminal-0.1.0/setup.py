#!/usr/bin/env python3

# To upload a version to PyPI, run:
#
#    python3 setup.py sdist upload
#
# If the package is not registered with PyPI yet, do so with:
#
# python3 setup.py register

from distutils.core import setup

VERSION = '0.1.0'

setup(name='interminal',
      version=VERSION,
      description='Utility for launching commands in a GUI terminal',
      author='Chris Billington',
      author_email='chrisjbillington@gmail.com',
      url='https://github.com/chrisjbillington/interminal',
      license="BSD",
      scripts=['bin/interminal', 'bin/inshell'])
