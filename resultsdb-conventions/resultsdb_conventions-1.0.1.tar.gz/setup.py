#!/usr/bin/env python
# Copyright (C) Red Hat, Inc.
#
# resultsdb_conventions is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author: Adam Williamson <awilliam@redhat.com>

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''
        self.test_suite = 'tests'

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args.split())
        sys.exit(errno)

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below. Stolen from
# https://pythonhosted.org/an_example_pypi_project/setuptools.html
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "resultsdb_conventions",
    version = "1.0.1",
    py_modules = ['resultsdb_conventions'],
    author = "Adam Williamson",
    author_email = "awilliam@redhat.com",
    description = "Module for conveniently reporting to ResultsDB following conventions",
    license = "GPLv3+",
    keywords = "fedora rhel epel resultsdb test taskotron",
    url = "https://pagure.io/fedora-qa/resultsdb_conventions",
    install_requires = ['cached-property', 'fedfind', 'resultsdb_api'],
    tests_require=['pytest', 'mock'],
    cmdclass = {'test': PyTest},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
    ],
)

# vim: set textwidth=120 ts=8 et sw=4:
