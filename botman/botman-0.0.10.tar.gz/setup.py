#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Installer and setup script
"""

from setuptools import setup

with open('README.rst') as readme_file:
    README = readme_file.read()

with open('HISTORY.rst') as history_file:
    HISTORY = history_file.read()

with open('requirements.txt') as requirements_file:
    REQUIREMENTS = requirements_file.readlines()

TEST_REQUIREMENTS = [
]

setup(
    name='botman',
    version='0.0.10',
    description="A Discord chat bot",
    long_description=README + '\n\n' + HISTORY,
    author="James Durand",
    author_email='james.durand@alumni.msoe.edu',
    url='https://github.com/durandj/botman',
    packages=[
        'botman',
    ],
    package_dir={'botman': 'botman'},
    entry_points={
        'console_scripts': [
            'botman=botman.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license="MIT license",
    zip_safe=False,
    keywords='botman',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
)

