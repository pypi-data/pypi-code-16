"""Setup module for WebserviceX-ConvertTemp.

see:
https://github.com/Yobota/WebserviceX-ConvertTemp
"""
from os.path import abspath
from os.path import dirname
from os.path import join
from re import search
from re import MULTILINE
from setuptools import find_packages
from setuptools import setup

HERE = abspath(dirname(__file__))

# NAME
NAME = 'webservicex_converttemp'

# VERSION
VERSION_PATH = join(HERE, 'webservicex_converttemp/version.py')
VERSION_LINE_PATTERN = r"^__version__ = ['\"]([^'\"]*)['\"]"

with open(VERSION_PATH, encoding='utf-8') as version_file:
    VERSION_FILE_CONTENTS = version_file.read()

VERSION_MATCH = search(VERSION_LINE_PATTERN, VERSION_FILE_CONTENTS, MULTILINE)
if VERSION_MATCH:
    VERSION = VERSION_MATCH.group(1)
else:
    MESSAGE = "Unable to find version string in {}.".format(VERSION_PATH)
    raise RuntimeError(MESSAGE)
# DESCRIPTON
DESCRIPTION = (
    'A Python client for the WebserviceX.NET Temperature Unit'
    'Converter webservice.')

# LONG_DESCRIPTION
README_PATH = join(HERE, 'README.rst')
with open(README_PATH, encoding='utf-8') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

# URL
URL = 'https://github.com/Yobota/WebserviceX-ConvertTemp'

# AUTHOR
AUTHOR = 'Yobota'
AUTHOR_EMAIL = 'daniel@yobota.xyz'

# LICENCE
LICENCE = 'MIT'

# CLASSIFIERS
CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
]

# KEYWORDS
KEYWORDS = 'temperature conversion webservice client'

# PACKAGES
PACKAGES = find_packages(exclude=['tests*'])

# INSTALL_REQUIRES
INSTALL_REQUIRES = []

setup(
    name=NAME,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    version=VERSION,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    licence=LICENCE,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
)
