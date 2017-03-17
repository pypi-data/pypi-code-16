#!/usr/bin/env python

import re
from os import path
from setuptools import setup, find_packages

setup(
    name='isoprene-pumpjack',
    version='0.0.4',
    license='Apache License 2.0',
    url='https://github.com/tommilligan/isoprene-pumpjack/',
    author='Tom Milligan',
    author_email='code@tommilligan.net',
    description="Backend for synaptic-scout; request data from Neo4j, perform searches in Elastic, and pump data between the two.",
    keywords='neo neo4j elastic elasticsearch graph iterative',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask >= 0.12',
        'Flask-RESTful >= 0.3.5',
        'Flask-cors >= 3.0.2',
        'gunicorn >= 19.6.0',
        'neo4j-driver >= 1.1.2',
        'elasticsearch-dsl >= 5.1.0',
        'certifi >= 2017.1.23'
    ],
    tests_require=['nose2 >= 0.6.5'],
    test_suite='nose2.collector.collector',
    # Install these with "pip install -e isoprene_pumpjack[dev]
    extras_require={
        'dev': [
            'sphinx >= 1.5.3',
            'sphinx-argparse >= 0.1.17',
            'sphinx_rtd_theme >= 0.1.9',
            'sphinxcontrib-httpdomain >= 1.5.0',
            'codeclimate-test-reporter >= 0.2.1',
            'cov-core >= 1.15.0',
            'nose2 >= 0.6.5',
            'coveralls >= 1.1'
        ]
    },
    entry_points={
        'console_scripts': [
            'isoprene-pumpjack = isoprene_pumpjack.api:main'
        ]
    },
)
