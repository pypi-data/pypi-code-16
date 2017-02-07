"""
WOFpy
-------

WOFpy is a python library for serving CUAHSI's WaterOneflow  web services

CUAHSI is the Consortium of Universities for the
Advancement of Hydrologic Science, Inc.

"""
import codecs
import os
import re

from setuptools import Command, setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")
import sys
if not sys.version_info[0] == 2:
    sys.exit("Sorry, Python 3 is not supported (yet)")
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    sys.exit("Sorry, Python  2.6 is not supported")
if sys.version_info[0] == 2 and sys.version_info[1] == 7 and sys.version_info[2] < 8 :
    sys.exit("Sorry, Issues with Python < 2.7.8. Please upgrade to 2.7.10 or above ")

setup(
    name='WOFpy',
    version=find_version("wof","__init__.py"),#'2.0.0005-alpha',
    license='BSD',
    author='James Seppi',
    author_email='james.seppi@gmail.com',
    # note: maintainer gets listed as author in PKG-INFO, so leaving
    # this commented out for now
    maintainer='David Valentine',
    maintainer_email='david.valentine@gmail.com',
    description='a python library for serving WaterOneFlow web services',
    long_description=__doc__,
    keywords='cuahsi his wofpy water waterml cuahsi wateroneflow odm2 czodata',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'flask>=0.10.0',
        'lxml>=3.4.4',
        'spyne>=2.12.8',
        'nose',
        'python-dateutil',
        'jinja2',
        'pytz'
    ],
    extras_require = {
        'odm1':  ["sqlalchemy", 'pyodbc'],
        'odm2':  ["sqlalchemy",'odm2api'],
        'sqlite': ["sqlalchemy"],
    },
    dependency_links=[
        "git+https://github.com/ODM2/geoalchemy.git@v0.7.3#egg=geoalchemy-0.7.3",
        "git+https://github.com/ODM2/ODM2PythonAPI@v0.1.0-alpha#egg=odm2api-0.1.0"
    ],
    tests_require=["suds", "requests"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],

)
