from distutils.core import setup
setup(
    name = 'sheetDB',
    packages = ['sheetDB'],
    install_requires = [
        'gspread==0.6.2',
        'oauth2client==4.0.0',
    ],
    version = '0.1.0',
    description = 'a library to use Google Sheets as a backend',
    author = 'knyte',
    author_email = 'galactaknyte@gmail.com',
    url = 'https://github.com/knyte/sheetDB',
    download_url = 'https://github.com/knyte/sheetDB/tarball/0.1.0',
    keywords = ['Google Sheets', 'spreadsheets', 'gspread'],
    classifiers = [],
)
