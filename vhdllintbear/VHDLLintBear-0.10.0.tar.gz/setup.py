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
        setup(name='VHDLLintBear',
              version='0.10.0',
              description=''''VHDLLintBear' bear for coala (http://coala.rtfd.org/)''',
              authors={'The coala developers'},
              authors_emails={'coala-devel@googlegroups.com'},
              maintainers={'The coala developers'},
              maintainers_emails={'coala-devel@googlegroups.com'},
              platforms={'any'},
              license='AGPL-3.0',
              packages=find_packages(exclude=['build.*']),
              install_requires=required,
              long_description='''
    Check VHDL code for common codestyle problems.

    Rules include:

     * Signals, variables, ports, types, subtypes, etc. must be lowercase.
     * Constants and generics must be uppercase.
     * Entities, architectures and packages must be "mixedcase" (may be 100%
       uppercase, but not 100% lowercase).
     * Ports must be suffixed using _i, _o or _io denoting its kind.
     * Labels must be placed in a separated line. Exception: component
       instantiation.
     * End statements must be documented indicating what are finishing.
     * Buffer ports are forbidden.
     * VHDL constructions of the "entity xxxx is" and similars must be in one
       line. You can't put "entity xxxxx" in one line and "is" in another.
     * No more than one VHDL construction is allowed in one line of code.

    See <http://fpgalibre.sourceforge.net/ingles.html#tp46> for more
    information.
    ''',
              entry_points={'coalabears': ['VHDLLintBear = coalaVHDLLintBear']},
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
