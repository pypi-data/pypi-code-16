from setuptools import setup

setup(
  name = 'statstable',
  packages = ['statstable'],
  version = '0.2',
  description = 'A wrapper to the StatStable API to retreive sports statistics',
  author = 'StatStable',
  author_email = 'info@statstable.com',
  url = 'https://github.com/statstable/statstable-python', 
  download_url = 'https://github.com/statstable/statstable-python/archive/0.2.tar.gz', 
  keywords = ['statstable', 'api', 'wrapper', 'sports', 'statistics', 'nba', 'mlb'],
  install_requires = [
    'requests',
  ],
  classifiers = [],
)
