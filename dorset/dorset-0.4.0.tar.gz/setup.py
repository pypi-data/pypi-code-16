# Copyright 2017 The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
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

from setuptools import setup

__version__ = '0.4.0'

setup(
    name='dorset',
    version=__version__,
    description='Package for implementing Dorset remote agent API',
    long_description=open('README.rst').read(),
    author='Cash Costello',
    author_email='cash.costello@gmail.com',
    url='https://github.com/DorsetProject/dorset-python',
    license='Apache Software License',
    py_modules=['dorset'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP'
    ],
    install_requires=['enum34;python_version<"3.4"']
)
