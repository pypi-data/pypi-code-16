#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# cms-booklet - github.com/obag/cms-booklet
# Copyright © 2014 Gabriele Farina <gabr.farina@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from setuptools import setup, find_packages
import os

PACKAGE_DATA = {
    "cmsbooklet.templates": [
        os.path.join("cms-contest", "*.*"),
        os.path.join("cms-contest", "data", "*.*"),
        os.path.join("cms-contest", "data", "locale", "*.*"),
    ],
}

setup(
    name = 'cmsbooklet',
    version = '0.7',
    description = 'cms-booklet: problem statement processor for CMS (Contest Management System)',
    author = 'Gabriele Farina',
    author_email = 'gabr.farina@gmail.com',
    packages=find_packages(),
    package_data=PACKAGE_DATA,
    entry_points={
        "console_scripts": [
            "cmsbooklet=cmsbooklet.cmsbooklet:main",
        ]
    },
    scripts=["scripts/mktesto"],
    install_requires=[
        "pyyaml",
        "jinja2",
    ],
)
