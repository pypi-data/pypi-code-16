# This file is part of python-munnel
# Copyright (C) 2017  Nexedi
# Author: Vincent Pelletier <vincent@nexedi.com>
#
# python-munnel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-functionfs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-munnel.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup
from codecs import open
import os

long_description = open(
    os.path.join(os.path.dirname(__file__), 'README.rst'),
    encoding='utf8',
).read()

setup(
    name='munnel',
    description=next(x for x in long_description.splitlines() if x.strip()),
    long_description='.. contents::\n\n' + long_description,
    keywords='smtp milter funnel',
    version='0.3',
    author='Nexedi',
    author_email='vincent@nexedi.com',
    url='https://lab.nexedi.com/nexedi/python-munnel',
    license='GPLv3',
    platforms=['any'],
    install_requires=['python-libmilter'],
    packages=['munnel'],
    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'munnel=munnel:main',
        ],
    }
)
