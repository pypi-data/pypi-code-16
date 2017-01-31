#!/usr/bin/env python3
"""Build a secure and RESTful hypermedia API."""


import re
import sys
from pathlib import Path
from setuptools import setup, find_packages

if sys.version_info < (3, 4):
    raise RuntimeError("hypr requires Python 3.4+")

# read the version number from package
with (Path(__file__).resolve().parent / 'hypr/__init__.py').open() as f:
    v, = re.search(".*__version__ = '(.*)'.*", f.read(), re.MULTILINE).groups()


setup(

    name='hypr',
    version=v,

    author='Morgan Delahaye-Prat',
    author_email='mdp@sillog.net',
    maintainer='Morgan Delahaye-Prat',
    maintainer_email='mdp@sillog.net',

    url='https://project-hypr.github.io',
    description=__doc__,
    long_description=open('README.rst').read(),

    install_requires=open('requirements.txt').read().splitlines(),
    tests_require=open('requirements_test.txt').read().splitlines(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=[],

    license='BSD',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]

)
