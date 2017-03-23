#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'twisted',
    'fs',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='tendril-server-fs',
    version='0.2.9',
    description="XML-RPC Filesystem Server using Twisted and Pyfilesystems for Tendril",
    long_description=readme,
    author="Chintalagiri Shashank",
    author_email='shashank@chintal.in',
    url='https://github.com/chintal/tendril-fs-server',
    packages=[
        'fs_server',
    ],
    package_dir={'fs_server': 'fs_server'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='tendril',
    classifiers=[
        'Development Status :: 4 - Beta',
        "License :: OSI Approved :: MIT License",
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
