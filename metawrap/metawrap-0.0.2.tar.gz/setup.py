#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
from setuptools import setup
import versioneer


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]


setup(
    name="metawrap",
    version=versioneer.get_version(),
    description="A collection of wrappers for functions and classes.",
    long_description=readme + "\n\n" + history,
    author="John Kirkham",
    author_email="kirkhamj@janelia.hhmi.org",
    url="https://github.com/jakirkham/metawrap",
    cmdclass=versioneer.get_cmdclass(),
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=requirements,
    license="BSD 3-Clause",
    zip_safe=False,
    keywords="metawrap",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=test_requirements
)
