#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='mixtract',
      version='3',
      description='Mixpanel data extraction / export tool',
      author='Mark Hyun-ki Kim',
      author_email='email@markhkim.com',
      license='MIT',
      url='https://github.com/markhkim/mixtract',
      download_url='https://github.com/markhkim/mixtract/tarball/2',
      keywords=['mixpanel'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6'
          ],
      install_requires=[
          'arrow', 'pandas', 'requests', 'sqlalchemy', 'pyyaml'],
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'mixtract = mixtract:main'
              ]
          },
      zip_safe=True
      )
