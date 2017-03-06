from distutils.core import setup
setup(
  name = 'wl_api',
  packages = ['wl_api'],
  install_requires=[
      'requests>=2.10.0',
  ],
  version = '0.1.5',
  description = 'a wrapper library for the Warlight API',
  author = 'knyte',
  author_email = 'galactaknyte@gmail.com',
  url = 'https://github.com/knyte/wl_api',
  download_url = 'https://github.com/knyte/wl_api/tarball/0.1.5',
  keywords = ['warlight', 'wrapper', 'api'],
  classifiers = [],
)
