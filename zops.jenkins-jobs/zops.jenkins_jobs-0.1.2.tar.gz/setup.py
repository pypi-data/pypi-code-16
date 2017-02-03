#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='zops.jenkins_jobs',
    use_scm_version=True,

    author="Alexandre Andrade",
    author_email='kaniabi@gmail.com',

    url='https://github.com/zerotk/zops.jenkins_jobs',

    description="Manage the creation of jenkins jobs.",
    long_description="Manage the creation of jenkins jobs.",

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
    packages=['zops', 'zops.jenkins_jobs'],
    namespace_packages=['zops'],
    entry_points="""
        [zops.plugins]
        main=zops.jenkins_jobs.cli:main
    """,
    install_requires=[
        'zerotk.zops',
        'jenkins-job-builder==2.0.0.0b1',
        'jenkins-job-builder-pipeline==0.1',
    ],
    dependency_links=[
        'https://github.com/rusty-dev/jenkins-job-builder-pipeline/tarball/master#egg=jenkins-job-builder-pipeline-0.1',
    ],
    setup_requires=['setuptools_scm'],
    tests_require=[],

    license="MIT license",
)
