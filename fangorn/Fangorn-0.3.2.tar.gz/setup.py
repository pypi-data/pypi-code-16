# -*- coding: utf-8 -*-
'''
@author: saaj
'''


try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


setup(
  name         = 'Fangorn',
  version      = '0.3.2',
  author       = 'saaj',
  author_email = 'mail@saaj.me',
  packages     = ['fangorn', 'fangorn.compat', 'fangorn.test',
    'fangorn.test.mysql', 'fangorn.test.sqlite'],
  package_data     = {'fangorn.test' : ['fixture/*.sql', 'fixture/fixture.py']},
  test_suite       = 'fangorn.test',
  url              = 'https://bitbucket.org/saaj/fangorn',
  license          = 'LGPL-2.1+',
  description      = 'Nested Sets SQL Tree for Python',
  long_description = open('README.txt', 'rb').read().decode('utf-8'),
  platforms        = ['Any'],
  extras_require   = {
    'pymysql'     : ['pymysql >= 0.6.1'],
    'mysqlclient' : ['mysqlclient >= 1.3.6']
  },
  keywords    = 'python tree nested-sets mysql sqlite',
  classifiers = [
    'Topic :: Database',
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Intended Audience :: Developers'
  ]
)