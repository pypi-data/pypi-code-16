#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
]

test_requirements = [
]

setup(
    name='dr-microservices',
    version='0.0.1',
    description="Microservices toolset to design, develop, and test microservices in a unified environment.",
    long_description=readme + '\n\n' + history,
    author="Ryan Anguiano",
    author_email='ryan.anguiano@gmail.com',
    url='https://github.com/ryananguiano/dr-microservices',
    packages=[
        'dr_microservices',
    ],
    package_dir={'dr_microservices': 'dr_microservices'},
    entry_points={
        'console_scripts': [
            'dr-micro=dr_microservices.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='dr-microservices',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
