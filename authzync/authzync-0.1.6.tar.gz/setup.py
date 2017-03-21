# -*- coding: utf-8 -*-

import io
import ast

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    """ Parses authzync.py and fetches the version attribute from the syntax tree
    :return: authzync version
    """
    with io.open('authzync.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s

with io.open('README.rst') as readme:
    setup(
        name='authzync',
        py_modules=['authzync'],
        version=get_version(),
        description='SVN AuthZ-LDAP sync tool',
        long_description=readme.read(),
        install_requires=['ldap3'],
        author='Robert Wikman',
        author_email='rbw@vault13.org',
        maintainer='Robert Wikman',
        maintainer_email='rbw@vault13.org',
        url='https://github.com/rbw0/authzync',
        download_url='https://github.com/rbw0/authzync/tarball/%s' % get_version(),
        keywords=['subversion', 'ldap', 'authz', 'sync'],
        platforms='any',
        classifiers=[
            'Programming Language :: Python',
        ],
        license='MIT',
    )
