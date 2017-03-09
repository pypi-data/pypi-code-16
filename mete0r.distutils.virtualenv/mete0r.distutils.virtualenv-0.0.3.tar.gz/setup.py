# -*- coding: utf-8 -*-
#
#   mete0r.distutils.virtualenv : Manage virtualenvs with requirement files
#   Copyright (C) 2015-2016 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or (at your
#   option) any later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#   License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import with_statement
from contextlib import contextmanager
import io
import os.path


def setup_dir(f):
    ''' Decorate f to run inside the directory where setup.py resides.
    '''
    setup_dir = os.path.dirname(os.path.abspath(__file__))

    def wrapped(*args, **kwargs):
        with chdir(setup_dir):
            return f(*args, **kwargs)

    return wrapped


@contextmanager
def chdir(new_dir):
    old_dir = os.path.abspath(os.curdir)
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


@setup_dir
def import_setuptools():
    try:
        import setuptools
        return setuptools
    except ImportError:
        pass

    import ez_setup
    ez_setup.use_setuptools()
    import setuptools
    return setuptools


@setup_dir
def readfile(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


@setup_dir
def get_version():
    from mete0r_distutils_virtualenv import __version__
    return __version__


def alltests():
    import sys
    import unittest
    import zope.testrunner.find
    import zope.testrunner.options
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    args = sys.argv[:]
    defaults = ['--test-path', here]
    options = zope.testrunner.options.get_options(args, defaults)
    suites = list(zope.testrunner.find.find_suites(options))
    return unittest.TestSuite(suites)


install_requires_filename = 'requirements-app.in'
install_requires = readfile(install_requires_filename)

tests_require = readfile('requirements-test.in')


setup_info = {
    'name': 'mete0r.distutils.virtualenv',
    'version': get_version(),
    'description': 'Manage virtualenvs with requirement files',
    'long_description': '\n'.join([readfile('README.rst'),
                                   readfile('CHANGES.rst')]),

    'author': 'mete0r',
    'author_email': 'mete0r@sarangbang.or.kr',
    'license': 'GNU Lesser General Public License v3 or later (LGPLv3+)',
    'url': 'https://github.com/mete0r/mete0r.distutils.virtualenv',

    'packages': [
        'mete0r_distutils_virtualenv',
        'mete0r_distutils_virtualenv.tests',
    ],
    # do not use '.'; just omit to specify setup.py directory
    'package_dir': {
        # '': 'src',
    },
    'package_data': {
        'mete0r_distutils_virtualenv': [
        ],
        # 'mete0r_distutils_virtualenv.tests': [
        #   'files/*',
        # ],
    },
    'install_requires': install_requires,
    'test_suite': '__main__.alltests',
    'tests_require': tests_require,
    'extras_require': {
        'test': tests_require,
    },
    'setup_requires': [
        'virtualenv >= 15.0.3',
    ],
    'entry_points': {
        'console_scripts': [
        ],
        'distutils.commands': [
            'virtualenv = mete0r_distutils_virtualenv.commands:virtualenv',
            ('virtualenv_bootstrap_script = '
             'mete0r_distutils_virtualenv.commands:'
             'virtualenv_bootstrap_script'),
            'pip_sync = mete0r_distutils_virtualenv.commands:pip_sync',
            'pip_compile = mete0r_distutils_virtualenv.commands:pip_compile',
        ],
        'zc.buildout': [
        ],
        'zc.buildout.uninstall': [
        ],
        'paste.app_factory': [
        ],
    },
    'classifiers': [
        'Development Status :: 3 - Alpha',
        # 'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',  # noqa
        # 'Operating System :: OS Independent',
        # 'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    'keywords': [
        'distutils',
        'virtualenv',
    ],
    'zip_safe': False,
}


@setup_dir
def main():
    setuptools = import_setuptools()
    from mete0r_distutils_virtualenv import commands

    setup_info['cmdclass'] = {
        'virtualenv': commands.virtualenv,
        'virtualenv_bootstrap_script': commands.virtualenv_bootstrap_script,
        'pip_sync': commands.pip_sync,
        'pip_compile': commands.pip_compile,
    }
    setuptools.setup(**setup_info)


if __name__ == '__main__':
    main()
