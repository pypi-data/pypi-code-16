#!/usr/bin/env python
from setuptools import setup

setup(
    name="TextReplace",
    version="1.0",
    description="Replaces all matched strings \
                in one directory with another",
    author="zenglifa",
    author_email="zenglifa@msu.edu",
    scripts=["bin/txt_replace"],
    packages=["txt_replace"],
    url="https://github.com/LeafyLi/txtreplace"
)