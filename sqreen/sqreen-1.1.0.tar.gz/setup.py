#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
import sqreen

long_description = """Sqreen is a SaaS based Application protection and monitoring platform that integrates directly into your Python applications.
Learn more at `<https://www.sqreen.io/>`_."""


setup(
    name='sqreen',
    version=sqreen.__version__,
    description="Sqreen agent to protect Python applications.",
    long_description=long_description,
    author="Boris Feld",
    author_email='boris@sqreen.io',
    url='https://github.com/sqreen/AgentPython',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'sqreen':
                 'sqreen'},
    package_data={'sqreen': ['*.crt']},
    include_package_data=True,
    install_requires=['py-mini-racer>=0.1.7'],
    license="Copyright",
    zip_safe=False,
    keywords='sqreen',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=[],
    entry_points={
        'console_scripts':  [
            "sqreen-start = sqreen.bin.protect:protect"
        ]
    }
)
