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
        setup(name='MypyBear',
              version='0.10.0',
              description=''''MypyBear' bear for coala (http://coala.rtfd.org/)''',
              authors={'Petr Viktorin'},
              authors_emails={'encukou@gmail.com'},
              maintainers={'Petr Viktorin'},
              maintainers_emails={'encukou@gmail.com'},
              platforms={'any'},
              license='AGPL-3.0',
              packages=find_packages(exclude=['build.*']),
              install_requires=required,
              long_description='''
    Type-checks your Python files!

    Checks optional static typing using the mypy tool.
    See <http://mypy.readthedocs.io/en/latest/basics.html> for info on how to
    add static typing.
    ''',
              entry_points={'coalabears': ['MypyBear = coalaMypyBear']},
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
