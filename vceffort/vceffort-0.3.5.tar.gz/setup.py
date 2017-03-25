
from setuptools import setup

setup(
  name = 'vceffort',
  version = '0.3.5',
  description = 'A script to estimate development hours from version control system log(s)',
  author = 'Tim Littlefair',
  author_email = 'tim_littlefair@hotmail.com',
  url = 'https://bitbucket.com/tim_littlefair/vceffort', # use the URL to the github repo
  license = 'MIT', 
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
  ],
  keywords = ['version control', 'metrics', 'example'], # arbitrary keywords
  install_requires = [ ],
  packages = ['vceffort'], 
  entry_points = { 'console_scripts' : [ 'vceffort=vceffort:main' ], },
)