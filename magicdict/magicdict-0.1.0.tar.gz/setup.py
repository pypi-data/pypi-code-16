#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2017 Kaede Hoshikawa
#
#   All rights reserved.

from setuptools import setup, find_packages

import importlib
import os
import sys

if not sys.version_info[:3] >= (3, 6, 0):
    raise RuntimeError("Magicdict requires Python 3.6.0 or higher.")


def load_version(module_name):
    _version_spec = importlib.util.spec_from_file_location(
        "{}._version".format(module_name),
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "{}/_version.py".format(module_name)))
    _version = importlib.util.module_from_spec(_version_spec)
    _version_spec.loader.exec_module(_version)
    return _version.version


setup_requires = ["setuptools", "pytest-runner>=2.11.1,<3"]

install_requires = []

tests_require = ["pytest>=3.0.6,<4"]

if __name__ == "__main__":
    setup(
        name="magicdict",
        version=load_version("magicdict"),
        author="Kaede Hoshikawa",
        author_email="futursolo@icloud.com",
        url="https://gitlab.com/futursolo/magicdict",
        license="Apache License 2.0",
        description="An ordered, one-to-many mapping.",
        long_description=open("README.rst", "r").read(),
        packages=find_packages(),
        include_package_data=True,
        setup_requires=setup_requires,
        install_requires=install_requires,
        tests_require=tests_require,
        extras_require={
            "test": tests_require
        },
        zip_safe=False,
        classifiers=[
            "Operating System :: MacOS",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Unix",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: Implementation :: CPython"
        ]
    )
