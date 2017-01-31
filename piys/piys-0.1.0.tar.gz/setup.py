#!/usr/bin/env python3


from setuptools import setup


setup(name='piys',
      version='0.1.0',
      description='',
      author='Steven J. Core',
      author_email='42Echo6Alpha@gmail.com',
      license='GPL3.0',
      packages=['piys'],
      zip_safe=False,
      include_package_data=True,
      install_requires=['requests'],
      entry_points={
        'console_scripts': [
            'piys = piys.piys:main'
         ]
      })
