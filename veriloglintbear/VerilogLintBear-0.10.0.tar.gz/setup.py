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
        setup(name='VerilogLintBear',
              version='0.10.0',
              description=''''VerilogLintBear' bear for coala (http://coala.rtfd.org/)''',
              authors={'The coala developers'},
              authors_emails={'coala-devel@googlegroups.com'},
              maintainers={'The coala developers'},
              maintainers_emails={'coala-devel@googlegroups.com'},
              platforms={'any'},
              license='AGPL-3.0',
              packages=find_packages(exclude=['build.*']),
              install_requires=required,
              long_description='''
    Analyze Verilog code using ``verilator`` and checks for all lint
    related and code style related warning messages. It supports the
    synthesis subset of Verilog, plus initial statements, proper
    blocking/non-blocking assignments, functions, tasks.

    It also warns about unused code when a specified signal is never sinked,
    and unoptimized code due to some construct, with which the
    optimization of the specified signal or block is disabled.

    This is done using the ``--lint-only`` command. For more information visit
    <http://www.veripool.org/projects/verilator/wiki/Manual-verilator>.
    ''',
              entry_points={'coalabears': ['VerilogLintBear = coalaVerilogLintBear']},
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
