from setuptools import setup, find_packages
import sys, os

version = '0.9'

setup(name='csnotifier',
      version=version,
      description="A product to send notifications to Pushwosh or Firebase",
      long_description="""Notification sender form django applications""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='CodeSyntax',
      author_email='info@codesyntax.com',
      url='https://codesyntax.com',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'requests'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
