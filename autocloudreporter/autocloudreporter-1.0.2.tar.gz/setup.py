# Copyright (C) Red Hat Inc.
#
# autocloudreporter is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:   Adam Williamson <awilliam@redhat.com>

"""Setuptools script."""

import os
from setuptools import setup, find_packages

# From: https://github.com/pypa/pypi-legacy/issues/148
# Produce rst-formatted long_description if pypandoc is available (to
# look nice on pypi), otherwise just use the Markdown-formatted one
try:
    import pypandoc
    longdesc = pypandoc.convert('README.md', 'rst')
except ImportError:
    longdesc = open('README.md').read()

setup(
    name = "autocloudreporter",
    version = "1.0.2",
    py_modules = ['autocloudreporter'],
    entry_points = {
        'moksha.consumer': (
            'autocloudreporter.prod = autocloudreporter:AutocloudReporter',
            'autocloudreporter.stg = autocloudreporter:AutocloudStagingReporter',
            'autocloudreporter.test = autocloudreporter:AutocloudTestReporter',
        ),
    },
    author = "Adam Williamson",
    author_email = "awilliam@redhat.com",
    description = ("Fedmsg consumer to report Autocloud results to ResultsDB"),
    license = "GPLv3+",
    keywords = "fedora qa autocloud resultsdb fedmsg",
    url = "https://pagure.io/fedora-qa/autocloudreporter",
    install_requires = open('install.requires').read().splitlines(),
    tests_require = open('tests.requires').read().splitlines(),
    long_description=longdesc,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
    ],
)

# vim: set textwidth=100 ts=8 et sw=4:
