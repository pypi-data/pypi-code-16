#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'queue_bqsr_status',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.11,
      description = 'write bqsr db status',
      url = 'https://github.com/NCI-GDC/queue_bqsr_status',
      license = 'Apache 2.0',
      packages = find_packages(),
      install_requires = [
          'pandas',
          'sqlalchemy'
      ],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['queue_bqsr_status=queue_bqsr_status.__main__:main']
          },
)
