# Copyright 2016 Quora, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

import codecs


VERSION = '0.3.0'


if __name__ == '__main__':
    with codecs.open('./README.rst', encoding='utf-8') as f:
        long_description = f.read()

    setup(
        name='qcore-nocython',
        version=VERSION,
        author='Quora, Inc.',
        author_email='asynq@quora.com',
        description='Quora\'s core utility library',
        long_description=long_description,
        url='https://github.com/quora/qcore',
        license='Apache Software License',
        classifiers = [
            'License :: OSI Approved :: Apache Software License',

            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
        keywords='quora core common utility',
        packages=find_packages(),
        install_requires=['six'],
    )

