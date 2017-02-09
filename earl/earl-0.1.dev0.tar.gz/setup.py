from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='earl',
      version=version,
      description="Tool for manipulating URL quea",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='url',
      author='n8',
      author_email='yo.its.n8@gmail.com',
      url='https://github.com/infin8/earl.py',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
