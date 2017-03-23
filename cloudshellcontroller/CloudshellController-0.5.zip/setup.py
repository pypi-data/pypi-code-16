from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
  name = 'CloudshellController',
  packages = find_packages(), # this must be the same as the name above
  version = '0.5',
  description = 'Quali API Wrapper',
  author = 'Joe Auby',
  author_email = 'joeyauby@gmail.com',
  url = 'https://github.com/Madslick/CloudshellController', # use the URL to the github repo
  download_url = 'https://github.com/Madslick/CloudshellController/archive/0.5.tar.gz', # I'll explain this in a second
  keywords = ['cloudshell', 'Quali', 'pypi', 'package'], # arbitrary keywords
  classifiers = [
  'Environment :: Console',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: MIT License',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Programming Language :: Python :: 2'
  ],
)