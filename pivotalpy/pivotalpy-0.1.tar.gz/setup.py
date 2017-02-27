#!/usr/bin/env python

from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
        name = "pivotalpy",
        version = "0.1",
        packages = find_packages(),
        install_requires = reqs,
        include_package_data=True,
        description = "Wrapper for Pivotal Tracker API v5",
        )
