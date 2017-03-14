"""Hello PyPI

A hello world package in python
"""

from setuptools import setup, find_packages

setup(
    name = "delta hello pypi",
    version = "0.0.3",
    description = "a simple python package",
    long_description = 'hello pypi, a simple python package',
    url = "https://github.com/delta4d/hello-pypi",
    author = "delta",
    email = "delta4d@gmail.com",
    license = "MIT",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    scripts = ["bin/hello"],
    keywords = "hello-world pypi setuptools",
    packages = find_packages(exclude = ["tests"])
)
