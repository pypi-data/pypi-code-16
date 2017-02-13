#!/usr/bin/env python

# Copyright 2017 Earth Sciences Department, BSC-CNS

# This file is part of the package bscearth.utils.

# The package package bscearth.utils is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

# The package bscearth.utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with bscearth.utils.  If not, see <http://www.gnu.org/licenses/>.
import os

from os import path
from setuptools import setup
from setuptools import find_packages

root = path.abspath(path.dirname(__file__))

# Get the version number from the relevant file
with open(path.join(root, 'VERSION')) as f:
    version = f.read().strip()

# -------------------------------------------------------------------------------
setup(
    namespace_packages=['bscearth'],
    name='bscearth.utils',
    version=version,
    description='Shared code and tools for various BSC-ES department projects (https://earth.bsc.es/wiki/)',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    author='CES Group at BSC-ES department',
    url='https://earth.bsc.es/gitlab/ces/bscearth.utils',
    download_url='https://earth.bsc.es/gitlab/ces/bscearth.utils/repository/archive.tar.gz?ref=v{0}'.format(version),
    packages=find_packages(exclude=['test']),
    author_email='ces@bsc.es',
    include_package_data=True,
    zip_safe=False,
    license='MIT', install_requires=['python-dateutil', 'pyparsing']
)
