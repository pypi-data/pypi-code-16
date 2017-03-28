# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 13 23:08:08 2016
"""

from setuptools import setup, find_packages
from simulator._version import __version__, __author__, __email__

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'

setup(
        name='simulator',
        version=__version__,
        description='Electrical Power System Simulator',
        license='MIT License',
        install_requires=[
                    'numpy',
                    'pandas',
                    'requests'
                ],
        author=__author__,
        author_email=__email__,
        packages=find_packages(),
        platforms='any',
)

