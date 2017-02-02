from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

# set version
__version__ = '0.0.9'

setup(
    name='pyqm',
    version=__version__,
    url='https://github.com/rh-marketingops/pyqm',
    license='GNU General Public License',
    author='Jeremiah Coleman',
    tests_require=['nose', 'mongomock>=3.6.0'],
    install_requires=['pymongo>=3.3.0', 'pyexecjs>=1.4.0'],
    author_email='colemanja91@gmail.com',
    description='Bulk queue management in MongoDB',
    #long_description=readme(),
    packages=['pyqm'],
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
        ],
    keywords = 'queue management mongo mongodb bulk'
)
