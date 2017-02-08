#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='zops.virtualenv',
    use_scm_version=True,

    author="Alexandre Andrade",
    author_email='kaniabi@gmail.com',

    url='https://github.com/zerotk/zops.virtualenv',

    description="Manage virtualenv generation, using cache when possible.",
    long_description="Manage virtualenv generation, using cache when possible.",

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
    packages=['zops', 'zops.virtualenv'],
    namespace_packages=['zops'],
    entry_points="""
        [zops.plugins]
        main=zops.virtualenv.cli:main
    """,
    install_requires=[
        'zerotk.zops',
        'zerotk.virtualenv-api',
    ],
    setup_requires=['setuptools_scm'],
    tests_require=[
        'pytest-click',
    ],

    license="MIT license",
)
