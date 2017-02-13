#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-wootric',
      version='0.1.0',
      description='Singer.io tap for extracting raw data from the Wootric API',
      author='Stitch',
      url='http://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_wootric'],
      install_requires=['stitchstream-python>=0.6.0',
                        'requests==2.12.4'],
      entry_points='''
          [console_scripts]
          tap-wootric=tap_wootric:main
      ''',
)

