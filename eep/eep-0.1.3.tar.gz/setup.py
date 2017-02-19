#!/usr/bin/env python

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

setup(name="eep",
      version="0.1.3",
      description=
      "Emacs style, point based string search-replace library for python",
      long_description=readme,
      author="Abhinav Tushar",
      author_email="abhinav.tushar.vs@gmail.com",
      url="https://github.com/lepisma/eep",
      include_package_data=True,
      install_requires=[],
      license="MIT",
      keywords="eep string search replace",
      packages=find_packages(exclude=["docs", "tests*"]),
      setup_requires=["pytest-runner"],
      tests_require=["pytest"])
