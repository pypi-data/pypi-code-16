#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
  name='wavshow',
  version='0.2',
  license='MIT',
  author="mzmttks",
  author_email="ta.mizumoto@gmail.com",
  url="https://github.com/mzmttks/wavshow",
  packages=find_packages(),
  insatll_requires=[
    "Click", "matplotlib", "numpy", "scipy"
  ],
  entry_points = {
    "console_scripts":{
      "wavshow=wavshow:main"
    }
  }
)
