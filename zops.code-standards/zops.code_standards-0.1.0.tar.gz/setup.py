#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='zops.code_standards',
    use_scm_version=True,

    author="Alexandre Andrade",
    author_email='kaniabi@gmail.com',

    url='https://github.com/zerotk/zops.code_standards',

    description="Apply and check for python code standards.",
    long_description="Apply and check for python code standards.",

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='development environment, shell, operations',

    include_package_data=True,
    packages=['zops', 'zops.code_standards'],
    namespace_packages=['zops'],
    entry_points="""
        [zops.plugins]
        main=zops.code_standards.cli:main
    """,
    install_requires=[
        'zerotk.zops',
        'isort',
        'autoflake',
        'autopep8',
    ],
    dependency_links=[
    ],
    setup_requires=['setuptools_scm'],
    tests_require=[],

    license="MIT license",
)
