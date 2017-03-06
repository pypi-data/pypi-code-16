#!/usr/bin/env python

# Copyright 2016 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup
import os
import re


VERSIONFILE = "fresco_fs.py"


def get_version():
    return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                     read(VERSIONFILE),
                     re.M).group(1)


def read(*path):
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')


setup(name='fresco-fs',
      version='0.1.dev0',
      description='Filesystem resources for fresco',
      long_description=read('README.rst') + "\n\n" + read("CHANGELOG.rst"),
      url='https://skot.be/',
      author='Oliver Cope',
      author_email='oliver@redgecko.org',
      license='Apache',
      install_requires=['fresco'],
      py_modules=['fresco_fs'],
      packages=[])
