#!/usr/bin/env python
import re
import os
import sys
from setuptools import setup


BASE = os.path.dirname(__file__)
README_PATH = os.path.join(BASE, 'README.rst')
CHANGES_PATH = os.path.join(BASE, 'CHANGES.rst')
long_description = '\n\n'.join((
    open(README_PATH).read(),
    open(CHANGES_PATH).read(),
))


setup(
    name='django-dartium',
    version='0.1.3',
    url='https://github.com/damoti/django-dartium',
    license='MIT',
    description='Django Middlware to detect Dartium web browser.',
    long_description=long_description,
    author='Lex Berezhny',
    author_email='lex@damoti.com',
    keywords='django,dart,dartium',
    classifiers=[
        'Framework :: Django',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Topic :: Software Development :: Testing',
	'Topic :: Software Development :: User Interfaces',
    ],
    packages=[
        'django_dartium',
        'django_dartium.templatetags',
    ],
)
