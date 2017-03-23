#!/usr/bin/python3
from setuptools import setup, find_packages

setup(name='climb',
      version='0.3.2',
      description='Library for interactive command line applications.',
      author='Milosz Smolka',
      author_email='m110@m110.pl',
      url='https://github.com/m110/climb',
      packages=find_packages(exclude=['tests']),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.4',
          'Topic :: System :: Systems Administration',
      ])
