# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import fnmatch
import os
import re
import sys

from setuptools import find_packages, setup, Command
from setuptools.command.install import install as InstallCommandBase
from setuptools.dist import Distribution

# This version string is semver compatible, but incompatible with pip.
# For pip, we will remove all '-' characters from this string, and use the
# result for pip.
_VERSION = '1.0.0'

project_name = 'yftest'

setup(
    name=project_name,
    version=_VERSION.replace('-', ''),
    description='Test',
    long_description='',
    # Contained modules and scripts.
    # PyPI package information.
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        ],
    license='Apache 2.0',
    keywords='machine learning',
    )
