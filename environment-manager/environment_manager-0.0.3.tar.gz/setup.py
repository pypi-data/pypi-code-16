""" Copyright (c) Trainline Limited, 2016. All rights reserved. See LICENSE.txt in the project root for license information. """
from setuptools import setup

setup(name='environment_manager',
      version='0.0.3',
      description="A Client library for Environment Manager",
      url="https://github.com/trainline/python-environment_manager",
      author="Marc Cluet",
      author_email="marc.cluet@thetrainline.com",
      install_requires=['requests', 'simplejson'],
      license='Apache 2.0',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5'],
      keywords='environment_manager client library development',
      package_data={'': ['LICENSE.txt']},
      packages=['environment_manager'],
      zip_safe=True)
