#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'urwid',
    'psutil'
]

test_requirements = [
    'flake8',
    'mock'
]

setup(
    name='topshape',
    version='0.2.0',
    description="Library for easily creating text interfaces that look like Linux's top program.",
    long_description=readme,
    author="Martin Chlumsky",
    author_email='martin.chlumsky@gmail.com',
    url='https://github.com/mchlumsky/topshape',
    packages=[
        'topshape',
    ],
    package_dir={'topshape':
                 'topshape'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='topshape',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='topshape.tests',
    tests_require=test_requirements,
    scripts=['bin/toppy']
)
