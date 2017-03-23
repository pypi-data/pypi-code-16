#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
import sys, os
"""
打包的用的setup必须引入，
"""

VERSION = '0.0.2'

setup(name='douban.cli',
      version=VERSION,
      description="A dead simple douban cli based on Python",
      long_description='just enjoy',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python douban douban.cli terminal',
      author='easonhan',
      author_email='nbkhic@qq.com',
      url='',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'clint',
        'requests',
      ],
      entry_points={
        'console_scripts':[
            'douban = douban.cli:main'
        ]
      },
)
