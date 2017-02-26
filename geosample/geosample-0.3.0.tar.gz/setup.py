#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'shapely>=1.5.17',
    'geojson>=1.3.3',
    'typing>=3.5.3.0',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='geosample',
    version='0.3.0',
    description="Sample locations from geospatial inputs",
    long_description=readme + '\n\n' + history,
    author="Jotham Apaloo",
    author_email='jothamapaloo@gmail.com',
    url='https://github.com/jo-tham/geosample',
    packages=[
        'geosample',
    ],
    package_dir={'geosample':
                 'geosample'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='geosample',
    entry_points = '''
      [console_scripts]
      geosample=geosample.cli:main
      ''',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
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
