# @copyright: AlertAvert.com (c) 2016. All rights reserved.

# https://github.com/pypa/sampleproject

from setuptools import setup

from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
#with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()
long_description = "AHG 48 from Eiheiji."

setup(name='ahg48',
      description='AHG 48',
      long_description=long_description,
      version='0.1.2',
      url='https://github.com/rch850/ahg48',
      author='rch850',
      author_email='rich850@gmail.com',
      license='Apache2',
      classifiers=[],
      packages=['ahg48'],
      entry_points={
          'console_scripts': [
              'encrypt=ahg48.main:run'
          ]
      }
)
