from distutils.core import setup
from setuptools import setup, find_packages

setup(
  name = 'magistral',
  packages = find_packages(),
  install_requires = ['pyjks>=0.5.1', 'requests>=2.12.3', 'paho--mqtt>=1.2', 'kafka>=1.3.1', 'pycrypto>=1.1.4', 'xxhash>=0.6.1', 'lz4>=0.8.1', 'lz4tools>=1.3.1.2'],
  version = '0.5.17',
  description = 'Python SDK for Magistral',
  author = 'Magistral.IO team',
  author_email = 'admin@magistral.io',
  url = 'https://github.com/magistral-io/MagistralPython',
  download_url = 'https://github.com/magistral-io/MagistralPython/tarball/0.5.17',
  keywords = [ 'magistral', 'sdk', 'messaging' ],
  classifiers = [],
)