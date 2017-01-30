#!/usr/bin/env python
import os
from setuptools import setup, find_packages

__version__ = '3.0.4'

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='raffaello',
      version=__version__,
      description='Raffaello command-line output colorizer',
      author='Carlo Lobrano',
      author_email='c.lobrano@gmail.com',
      license="MIT",
      long_description = read('README.rst'),
      url='https://github.com/clobrano/raffaello',
      keywords=['formatter', 'console', 'colorizer'],
      classifiers=[
           "Development Status :: 5 - Production/Stable",
           "Topic :: Utilities",
           "Topic :: System :: Logging",
      ],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=['docopt', ],

      py_modules=['raffaello'],
      entry_points={
          'console_scripts': ['raffaello=raffaello:main'],
      },
      include_package_data=True,
      )
