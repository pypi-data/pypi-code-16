# -*- coding: utf-8 -*-
"""
Flask-Humanoid
==============

Extension provides common humanization utilities, like turning number into a
fuzzy human-readable duration or into human-readable size, to your flask
application.

"""
from setuptools import setup

setup(
    name='Flask-Humanoid',
    version='1.0',
    author='Bapakode Open Source',
    author_email='opensource@bapakode.org',
    url="http://bapakode.org/flask-humanoid",
    description='Common humanization utilities for Flask applications.',
    license='MIT',
    packages=['flask_humanoid'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'humanize',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
