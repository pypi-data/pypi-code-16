# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.md").read()
except IOError:
    long_description = """
"""

setup(
    name="configus",
    version="0.1.1",
    description="Configus - a declarative spec for configuration",
    license="MIT",
    author="Alex Myasoedov",
    author_email="msoedov@gmail.com",
    packages=['configus'],
    install_requires=['trafaret'],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ]
)
