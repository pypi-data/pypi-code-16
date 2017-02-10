# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name="openwhisk_docker_action",
    version="0.1.0",
    description="A class to make writing openwhisk docker actions easier to write in python",
    license="MIT",
    author="Joshua B. Smith",
    author_email='kognate@gmail.com',
    url='https://github.com/kognate/openwhisk_docker_action',
    packages=find_packages(),
    install_requires=[ 'flask' ],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ]
)
