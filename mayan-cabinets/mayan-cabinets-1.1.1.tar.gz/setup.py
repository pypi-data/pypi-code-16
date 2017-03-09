#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(
    author='Roberto Rosario',
    author_email='roberto.rosario@mayan-edms.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    description='Multi level document hierachy app for Mayan EDMS.',
    include_package_data=True,
    install_requires=('django-mptt==0.8.7',),
    license='Apache 2.0',
    long_description=readme + '\n\n' + history,
    name='mayan-cabinets',
    package_data={'': ['LICENSE']},
    package_dir={'cabinets': 'cabinets'},
    packages=[
        'cabinets', 'cabinets.compat', 'cabinets.migrations', 'cabinets.tests'
    ],
    platforms=['any'],
    url='https://gitlab.com/mayan-edms/cabinets',
    version='1.1.1',
    zip_safe=False,
)
