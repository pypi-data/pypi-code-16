#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='django_heroku_db_utils',
    version='0.1.0',
    description="A package with a few utilities for accessing Heroku DB instances",
    long_description=readme + '\n\n' + history,
    author="Nahuel Defosse",
    author_email='nahuel.defosse@gmail.com',
    url='https://github.com/D3f0/django_heroku_db_utils',
    packages=[
        'django_heroku_db_utils',
    ],
    package_dir={'django_heroku_db_utils':
                 'django_heroku_db_utils'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='django_heroku_db_utils',
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
