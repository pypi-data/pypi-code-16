#!/usr/bin/env python

import os
import os.path
from setuptools import setup

os.chdir(os.path.abspath(os.path.dirname(__file__)))

setup(
    version="0.1.2",
    url="https://github.com/nathforge/ap",
    name="ap",
    description="AP powers-up commands with AWS profile, assume-role and MFA functionality.",
    long_description=open("README.rst").read(),
    author="Nathan Reynolds",
    author_email="email@nreynolds.co.uk",
    packages=["ap"],
    package_dir={"": "src"},
    install_requires=["botocore"],
    entry_points={
        "console_scripts": [
            "ap = ap:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5"
    ]
)
