"""
Setup for Import.io Google Sheet Extractor Integration
"""
from setuptools import setup
import re

PACKAGE = 'importio_gsei'
VERSION_FILE = "importio_gsei/version.py"
verstrline = open(VERSION_FILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSION_FILE,))

setup(
    name='importio_gsei',
    version=version,
    url='http://github.io/import.io/google-sheets-extractor-integration',
    author='David Gwartney',
    author_email='david.gwartney@import.io',
    packages=['importio_gsei', ],
    license='LICENSE',
    entry_points={
        'console_scripts': [
            'gsextractor = importio_gsei.main:main',
        ],
    },
    description='Command line to feed URLs from a Google Sheet into an Import.io Extractor',
    long_description=open('README.txt').read(),
    install_requires=[
        'google-api-python-client>=1.6.1',
        'httplib2==0.10.3',
        'requests >= 2.13.0',
    ],
)

