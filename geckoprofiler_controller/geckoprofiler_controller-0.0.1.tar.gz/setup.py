#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages

VERSION = '0.0.1'
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

# dependencies
DEFAULT_REQUIREMENT_DOC = os.path.join(CURRENT_PATH, 'requirements.txt')
with open(DEFAULT_REQUIREMENT_DOC) as f:
    deps = f.read().splitlines()

# get documentation from the README and HISTORY
try:
    with open(os.path.join(CURRENT_PATH, 'README.rst')) as doc:
        readme = doc.read()
except:
    readme = ''

try:
    with open(os.path.join(CURRENT_PATH, 'HISTORY.rst')) as doc:
        history = doc.read()
except:
    history = ''

long_description = readme + '\n\n' + history

# main setup script
setup(
    name='geckoprofiler_controller',
    version=VERSION,
    description='Control the Gecko Profiler by Python and Web Socket',
    long_description=long_description,
    author='Askeing Yen',
    author_email='askeing@gmail.com',
    url='https://github.com/askeing/gecko-profiler-controller',
    keywords='mozilla firefox gecko profiler utilities ',
    license='MPL',
    install_requires=deps,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
