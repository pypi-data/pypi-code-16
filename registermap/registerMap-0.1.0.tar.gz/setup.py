#
# Copyright 2017 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath( path.dirname( __file__ ) )

try :
    import pypandoc


    long_description = pypandoc.convert( 'README.rst', 'rst' )
except OSError :
    print( "Pypandoc not found. Long_description conversion failure." )
    # pandoc is not installed, fallback to using raw contents
    with open( 'README.md', encoding = "utf-8" ) as f :
        long_description = f.read( )

setup(
    name = 'registerMap',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version = '0.1.0',

    description = 'YAML based register map definitions for digital hardware and embedded software development',
    long_description = long_description,

    # The project's main homepage.
    url = 'https://gitlab.com/blueskyjunkie/registerMap',

    # Author details
    author = 'Russell Smiley',
    author_email = 'im.russell.smiley@gmail.com',

    license = 'GPLV3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Hardware',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords = 'registermap buildtools development hardware digital register',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages = find_packages( exclude = [ 'contrib', 'doc', '*tests*' ] ),
    setup_requires = [
        'setuptools',
        'setuptools-git',
        'wheel',
    ],

    # These will be installed by pip when your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [ 'pyyaml' ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require = {
        'dev' : [ 'zest.releaser[recommended]',
                  'Sphinx',
                  'setuptools',
                  'setuptools-git' ],
        'test' : [ 'nose',
                   'nose-exclude', ],
    },

    zip_safe = False,

)
