# -*- coding: utf-8 -*-

"""
@author: MonsterDeveloper
@contact: https://github.com/MonsterDeveloper
@license: MIT License, see LICENSE file

Copyright (C) 2017
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name='telegraphapi',
      description='Python TelegraphAPI)',
      url='https://github.com/MonsterDeveloper/python-telegraphapi',
      author="Andrew Developer",
      author_email="slider7259@gmail.com",
      packages=['telegraphapi'],
      install_requires=[
          'requests',
      ],
      license="MIT",
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython'
      ],
      zip_safe=False,
      version="0.2",
      include_package_data=True,
      keywords='telegraph api rest http telegraphapi telegram')