#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'table_string_sqlite_cell',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.2,
      description = 'create a single cell table with a value',
      url = 'https://github.com/NCI-GDC/table_string_sqlite_cell',
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
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['table_string_sqlite_cell=table_string_sqlite_cell.__main__:main']
          },
)
