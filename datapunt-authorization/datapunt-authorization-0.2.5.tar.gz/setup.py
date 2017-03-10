#!/usr/bin/env python

import sys

from codecs import open

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """ Custom class to avoid depending on pytest-runner.
    """
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

packages = ['authorization']

# The 'click' and 'crayons' libraries are needed so Evert can avoid using
# argparse and have colored CLI output. :(
requires = [
    'datapunt-authorization-levels',
    'psycopg2>=2.6.2',
    'click>=6.7',
    'crayons'
]
requires_test = ['pytest>=3.0.5', 'pytest-cov>=2.4.0']

setup(
    name='datapunt-authorization',
    version='0.2.5',
    description='Datapunt authorization',
    long_description=long_description,
    url='https://github.com/DatapuntAmsterdam/authorization',
    author='Amsterdam Datapunt',
    author_email='datapunt.ois@amsterdam.nl',
    license='Mozilla Public License Version 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass={'test': PyTest},
    packages=packages,
    install_requires=requires,
    tests_require=requires_test,
    entry_points={'console_scripts': [
        'authz = authorization.cli:cli',
    ]},
)
