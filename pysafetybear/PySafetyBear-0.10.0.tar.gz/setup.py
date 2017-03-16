#!/usr/bin/env python3
import os
import locale

from setuptools import find_packages, setup


try:
    locale.getlocale()
except (ValueError, UnicodeError):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

required = ''
if os.path.exists('requirements.txt'):
    with open('requirements.txt') as requirements:
        required = requirements.read().splitlines()

if __name__ == '__main__':
    try:
        setup(name='PySafetyBear',
              version='0.10.0',
              description=''''PySafetyBear' bear for coala (http://coala.rtfd.org/)''',
              authors={'Bence Nagy'},
              authors_emails={'bence@underyx.me'},
              maintainers={'Bence Nagy'},
              maintainers_emails={'bence@underyx.me'},
              platforms={'any'},
              license='AGPL',
              packages=find_packages(exclude=['build.*']),
              install_requires=required,
              long_description='''
    Checks if any of your Python dependencies have known security issues.

    Data is taken from pyup.io's vulnerability database hosted at
    https://github.com/pyupio/safety.
    ''',
              entry_points={'coalabears': ['PySafetyBear = coalaPySafetyBear']},
              classifiers=[
                   'Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Environment :: Win32 (MS Windows)',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'Programming Language :: '
                   'Python :: Implementation :: CPython',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Software Development :: Quality Assurance',
                   'Topic :: Text Processing :: Linguistic'])

    finally:
        print('[WARN] If you do not install the bears using the coala '
              'installation tool, there may be problems with the dependencies '
              'and they may not work.')
