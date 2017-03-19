#!/usr/bin/env python
from setuptools import setup

readme_file = open('README.rst')
long_description = readme_file.read()

setup(name="asyncrandom",
      description="Async random number generator.",
      version="0.0.1",
      author="Yavor Paunov",
      long_description=long_description,
      author_email='contact@yavorpaunov.com',
      license='MIT',
      entry_points={
          "console_scripts": ["asyncrandom=asyncrandom:main"]
      },
      install_requires=["tornado>=4.4", "enum34"],
      tests_require=["mock"],
      py_modules=["asyncrandom"],
      test_suite="tests")
