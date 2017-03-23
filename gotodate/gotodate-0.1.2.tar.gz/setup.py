#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
 
import sys
if sys.version_info < (2, 5):
    sys.exit('Python 2.5 or greater is required.')
 
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
import gotodate
 
 
#with open('README.md') as fp:
#    readme = fp.read()
 
#with open('LICENSE') as fp:
#    license = fp.read()
 
setup(name='gotodate',
      version=gotodate.__version__,
      description=u'获取某天，前N天，后N天，当前日期周几，当前日期所在周的周一至周日日期',
      long_description="",
      author='Shancang Chen',
      author_email='chenshancang@163.com',
      maintainer='Shancang Chen',
      maintainer_email='chenshancang@163.com',
      url='https://github.com/shancang/pythonlib.git',
      packages=['gotodate'],
      license="",
      platforms=['any'],
      classifiers=[]
      )