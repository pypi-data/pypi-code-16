#!/usr/bin/env python

import re
import sys
from os import path
from setuptools import setup, find_packages

PY26 = sys.version_info[:2] == (2, 6,)

requirements = [
    'aniso8601>=0.82',
    'Flask>=0.8',
    'six>=1.3.0',
    'pytz',
]

if PY26:
    requirements.append('ordereddict')


version_file = path.join(
    path.dirname(__file__),
    'flask_restbolt',
    '__version__.py'
)

with open(version_file, 'r') as fp:
    m = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        fp.read(),
        re.M
    )
    version = m.groups(1)[0]


setup(
    name='Flask-RESTbolt',
    version=version,
    license='BSD',
    url='https://github.com/costular/flask-restbolt/',
    author='Costular',
    author_email='costular@gmail.com',
    description='Powerful and fast framework for creating REST APIs with Flask',
    packages=find_packages(exclude=['tests']),
    keywords=['flask rest', 'flask restful', 'restbolt', 'flask restbolt', 'flask api', 'flask api rest'],
    classifiers=[
        'Framework :: Flask',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    install_requires=requirements,
    tests_require=['Flask-RESTbolt[paging]', 'mock>=0.8', 'blinker'],
    # Install these with "pip install -e '.[paging]'" or '.[docs]'
    extras_require={
        'paging': 'pycrypto>=2.6',
        'docs': 'sphinx',
    }
)
