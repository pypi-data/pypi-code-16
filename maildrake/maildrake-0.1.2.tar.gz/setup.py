# setup.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Distribution setup for Mail Drake application. """

import os.path
import pydoc
import sys
import unittest

from setuptools import (setup, find_packages)


if sys.version_info < (3,):
    print("Mail Drake requires Python 3 or later.")
    sys.exit(1)


main_module_name = 'maildrake'
main_module_fromlist = ['_metadata']
main_module = __import__(
        main_module_name,
        level=0, fromlist=main_module_fromlist)
metadata = main_module._metadata

(synopsis, long_description) = pydoc.splitdoc(pydoc.getdoc(main_module))


def test_suite():
    """ Make the test suite for this code base. """
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.curdir, pattern='test_*.py')
    return suite


setup(
        name=metadata.distribution_name,
        version=metadata.version_text,
        packages=find_packages(exclude=["test"]),
        package_data={
            main_module_name: ['VERSION'],
            },

        # Setuptools metadata.
        zip_safe=False,
        setup_requires=[
            "docutils",
            "semver",
            ],
        test_suite='setup.test_suite',
        tests_require=[
            "testtools",
            "testscenarios >=0.4",
            "Faker",
            "docutils",
            "semver",
            "sqlparse",
            "fasteners",
            ],
        install_requires=[
            "setuptools",
            # Docutils is only required for building, but Setuptools
            # can't distinguish dependencies properly.
            # See <URL:https://github.com/pypa/setuptools/issues/457>.
            "docutils",
            "semver",
            "sqlparse",
            "fasteners",
            ],
        entry_points={
            'console_scripts': [
                'maildrake-smtp = maildrake.smtp.service:main',
                'maildrake-web = maildrake.web.service:main',
            ],
        },

        # PyPI metadata.
        author=metadata.author_name,
        author_email=metadata.author_email,
        description=synopsis,
        license=metadata.license,
        keywords="email smtp queue debug".split(),
        url=metadata.url,
        long_description=long_description,
        classifiers=[
            # Reference: https://pypi.python.org/pypi?:action=list_classifiers
            "Development Status :: 4 - Beta",
            (
                "License :: OSI Approved ::"
                " GNU Affero General Public License v3 or later (AGPLv3+)"),
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Topic :: Communications :: Email :: Mail Transport Agents",
            "Topic :: Software Development :: Testing",
            ],
        )


# Copyright © 2008–2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.AGPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
