from distutils.core import setup
setup(
    name = 'wl_parsers',
    packages = ['wl_parsers'],
    install_requires = [
        'requests>=2.10.0',
    ],
    version = '0.1.2',
    description = 'a library to parse the Warlight.net site',
    author = 'knyte',
    author_email = 'galactaknyte@gmail.com',
    url = 'https://github.com/knyte/wl_parsers',
    download_url = 'https://github.com/knyte/wl_parsers/tarball/0.1.2',
    keywords = ['warlight', 'parser', 'scraping'],
    classifiers = [],
)
