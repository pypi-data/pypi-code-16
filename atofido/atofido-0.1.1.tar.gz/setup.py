#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from setuptools import setup
from setuptools import find_packages

here = path.abspath(path.dirname(__file__))

# Get the version number from the relevant file
with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()

setup(
    name='atofido',
    license='MIT',
    version=version,
    description='Atofido is a plugin-based automatic torrent files downloader',
    author='Joan López de la Franca Beltran',
    author_email='joanjan14@gmail.com',
    url='https://github.com/joanlopez/atofido',
    keywords=['downloader', 'automatic', 'torrent'],
    install_requires=['mock>=1.3.0', 'Yapsy>=1.11.223'],
    packages=find_packages(),
    include_package_data=True,
    package_data={'atofido':
        [
            'README',
            'VERSION',
            'LICENSE'
        ]
    },
    scripts=['bin/atofido']
)
