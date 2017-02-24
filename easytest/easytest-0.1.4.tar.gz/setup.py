# -*- coding: UTF-8 -*-

# good introduction into packing can be found in
# https://python-packaging-user-guide.readthedocs.org/en/latest/index.html

from setuptools import setup
# from distutils.core import setup as setup_dist  # todo use only one setup

#import os
#import glob

# the setuptools are supposed to be used as a standard. Thats why we ommit
# usage of distutils here

# example of setup.py can be found here:
# https://github.com/pypa/sampleproject/blob/master/setup.py

# a small example how to build dependencies is given here:
# http://stackoverflow.com/questions/11010151/distributing-a-shared-library-and-some-c-code-with-a-cython-extension-module

#import os
#import numpy as np
#import json

from setuptools import find_packages  # Always prefer setuptools over distutils
#~ from Cython.Distutils import build_ext

install_requires = ["numpy>1.0", "netCDF4"]




def get_packages():
    return find_packages()


setup(name='easytest',

      version='0.1.4',

      description='easytest - a framework for simple automated testing',

      # You can just specify the packages manually here if your project is
      # simple. Or you can use find_packages().
      # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

      packages=get_packages(),
      package_dir={'easytest': 'easytest'},
      #~ package_data={'pycmbs': ['benchmarking/configuration/*',
                               #~ 'benchmarking/logo/*', 'version.json']},

      author="Alexander Loew",
      author_email='alexander.loew@lmu.de',
      maintainer='Alexander Loew',
      maintainer_email='alexander.loew@lmu.de',

      license='APACHE 2.0',

      long_description='No long description so far',

      # List run-time dependencies here. These will be installed by pip when your
      # project is installed. For an analysis of "install_requires" vs pip's
      # requirements files see:
      # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
      #~ install_requires=install_requires,

      keywords=["testing", "science"],


      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[

          'Programming Language :: Python :: 2.7'
      ],

      #~ ext_modules=[ext_polygon_utils, ext_variogramm],
      #cmdclass={'build_ext': build_ext}
      #~ cmdclass={'build_ext': CustomExtBuild}
      )




########################################################################
# Some useful information on shipping packages
########################################################################

# PIP
# 1) on a new computer you need to create a .pypirc file like described in the
# pypi documentation
# 2) install twine using pip install twine
# 3) generate package using: python setup.py sdist
# 4) just upload using twine upload dist/*
