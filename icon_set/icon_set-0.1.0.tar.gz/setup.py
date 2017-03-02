#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'Pillow==4.0.0',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='icon_set',
    version='0.1.0',
    description="Utility tool to help you create Apple Icon Set files.",
    long_description=readme + '\n\n' + history,
    author="Shahriar Tajbakhsh",
    author_email='sh.tajbakhsh@gmail.com',
    url='https://github.com/s16h/icon_set',
    packages=[
        'icon_set',
    ],
    package_dir={'icon_set':
                 'icon_set'},
    entry_points={
        'console_scripts': [
            'icon_set=icon_set.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='icon_set',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
