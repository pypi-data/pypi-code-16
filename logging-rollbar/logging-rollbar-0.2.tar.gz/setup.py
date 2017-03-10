import setuptools
from distutils.core import setup
setup(
  name = 'logging-rollbar',
  packages = ['logging_rollbar'], 
  install_requires = ['rollbar'],
  version = '0.2',
  description = 'An implementation of the python logging library with support for rollbar',
  author = 'Alex Cowan',
  author_email = 'alex@razorsecure.com',
  url = 'https://github.com/lucien2k/logging-rollbar',
  download_url = 'https://github.com/lucien2k/logging_rollbar/archive/0.2.tar.gz', # I'll explain this in a second
  keywords = ['logging', 'rollbar'], # arbitrary keywords
  license="MIT",
  classifiers = [],
)
