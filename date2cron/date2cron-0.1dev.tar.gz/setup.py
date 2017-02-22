from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='date2cron',
      version=version,
      description="date2cron",
      long_description="convert date to a cron expression",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='cron',
      author='yafeile',
      author_email='yafeile@sohu.com',
      url='https://bitbucket.org/yafeile/date2cron',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True
      )
