# -*- coding: utf-8 -*-

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

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from geofluent import __version__

_description = "Unnoficial Python Client to access the GeoFluent API"
try:
    _long_description = open('README.md').read()
except IOError:
    _long_description = _description  # TODO

try:
    with open('requirements.txt', 'r') as f:
        _install_requires = [line.rstrip('\n') for line in f]
except IOError:
    _install_requires = []  # TODO
    
setup(
    name="geofluent",
    version=__version__,
    author="Sergio Fernández",
    author_email="sergio.fernandez@redlink.co",
    description=_description,
    packages=['geofluent'],
    long_description=_long_description,
    platforms=['any'],
    install_requires=_install_requires,
    entry_points={
        'console_scripts': [
            'geofluent = geofluent.cli:main'
        ]
    },
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Topic :: Software Development :: Libraries',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Environment :: Console'],
    keywords='client api translation geofluent ssix',
    use_2to3=True
)
