import os
from setuptools import setup

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = open(os.path.join(here, 'README.txt')).read()
except IOError:
    description = None

version = '0.0'

deps = []

setup(name='whichpy',
      version=version,
      description="python equivalent of which",
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='https://pypi.python.org/pypi/whichpy',
      license='',
      py_modules=['which'],
      packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=deps,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      which.py = which:main
      """,
      )

