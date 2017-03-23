#!/usr/bin/env python
#
# Copyright (c) 2009 Heikki Toivonen <my first name at heikkitoivonen.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import os
import codecs
from setuptools import setup, find_packages


version = '1.0'


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    print('You probably want to also tag the version now:')
    print('  git tag -a %s -m "version %s"' % (version, version))
    print('  git push --tags')
    sys.exit()


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


install_requires = [
    'cryptography>=1.8.1',
]


test_requires = [
    'pytest==3.0.7',
    'pytest-flakes==1.0.1',
    'pytest-pep8==1.0.6',
    'pep8==1.4.6',
    'mock==2.0.0',
]


setup(
    name='m2secret-py3',
    version=version,
    description='Encryption and decryption module and CLI utility. Python 2 and 3 compatible.',
    long_description=read('README.rst'),
    author='Heikki Toivonen',
    author_email='My first name at heikkitoivonen.net',
    maintainer='Christopher Grebs',
    maintainer_email='cg@webshox.org',
    url='https://github.com/EnTeQuAk/m2secret',
    license='Apache Software License',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'tests': test_requires,
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'm2secret = m2secret:main'
        ]
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security :: Cryptography',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: Django',
    ]
)
