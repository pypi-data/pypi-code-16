#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README') as readme_file:
    readme = readme_file.read()

with open('HISTORY') as history_file:
    history = history_file.read()

requirements = [
    'click',
    'pyexcel',
    'pyexcel-xlsx',
    'SQLAlchemy',
]

test_requirements = [
    'mock',
]

setup(
    name='pyreportxl',
    version='0.1.0',
    description="An Excel reporting framework for python.",
    long_description=readme + '\n\n' + history,
    author="Chris Pappalardo",
    author_email='cpappala@yahoo.com',
    url='https://github.com/ChrisPappalardo/pyreportxl',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyreportxl=pyreportxl.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyreportxl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
