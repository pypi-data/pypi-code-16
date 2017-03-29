from distutils.core import setup
from setuptools import find_packages
setup(
    name = 'sheetDB',
    packages = find_packages('sheetDB', exclude=['test',]),
    install_requires = [
        'gspread>=0.6.2',
        'oauth2client>=4.0.0',
        'PyOpenSSL',
    ],
    version = '0.1.5',
    description = 'a library to use Google Sheets as a backend',
    author = 'knyte',
    license = 'MIT',
    author_email = 'galactaknyte@gmail.com',
    url = 'https://github.com/knyte/sheetDB',
    download_url = 'https://github.com/knyte/sheetDB/tarball/0.1.5',
    keywords = ['Google Sheets', 'spreadsheets', 'gspread'],
    classifiers = [],
)
