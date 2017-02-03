#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'queue_hlatype_status',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.09,
      description = 'write hlatyping db status',
      url = 'https://github.com/jeremiahsavage/queue_hlatype_status',
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
          'console_scripts': ['queue_hlatype_status=queue_hlatype_status.__main__:main']
          },
)
