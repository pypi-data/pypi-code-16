#!/usr/bin/env python
import pyvss

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def required():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def read(filename):
    return open(filename).read()

setup(name='pyvss',
      version=pyvss.__version__,
      description='Python client for the EIS Virtual Cloud RESTful API',
      long_description=read('README.rst'),
      author='University of Toronto - EIS - VSS',
      author_email='jm.lopez@utoronto.ca',
      maintainer='JM Lopez',
      maintainer_email='jm.lopez@utoronto.ca',
      url='https://gitlab.eis.utoronto.ca/vss/py-vss',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.5',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      license='MIT License',
      packages=['pyvss'],
      download_url='https://gitlab.eis.utoronto.ca/vss/py-vss',
      platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix', 'OpenBSD'],
      install_requires=required()
      )
