#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requisites = []

setup(
    name='saltfm',
    version='0.0.3',
    description='Salt Formula Manager',
    scripts=['scripts/saltfm'],
    long_description=open('README.rst').read(),
    author='Viet Hung Nguyen',
    author_email='hvn@familug.org',
    url='https://github.com/hvnsweeting/saltfm',
    packages=['saltfm'],
    data_files=[('share/saltfm', ['README.rst', 'config.yaml.sample'])],
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
    ],
)
