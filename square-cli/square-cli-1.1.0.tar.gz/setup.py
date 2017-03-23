#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="square-cli",
    version="1.1.0",
    author="MOS team",
    author_email="mos-scale@mirantis.com",

    description="This is a CLI for square project",
    license="BSD",
    url="http://gerrit.mirantis.com/a/mos-scale/square",

    scripts=['inventory.py'],

    install_requires=[
        'requests==2.11.1'
    ],
)
