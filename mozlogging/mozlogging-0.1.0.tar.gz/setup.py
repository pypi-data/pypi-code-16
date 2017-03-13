#!/usr/bin/env python
import re

from codecs import open
from setuptools import setup, find_packages


requires = []

with open('mozlogging/__init__.py', 'r') as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        f.read(),
        re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version')

with open('README.rst', 'r', 'utf-8') as f:
    description = f.read()

setup(
    name='mozlogging',
    version=version,
    description='MozLog with the logging Module',
    long_description=description,
    author='Steven MacLeod',
    author_email='smacleod@mozilla.com',
    url='https://github.com/smacleod/mozlogging',
    packages=find_packages(exclude=['docs', 'tests']),
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    license='MPL 2.0',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ),
)
