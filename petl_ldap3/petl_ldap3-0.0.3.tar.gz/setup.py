#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from petl_ldap3._version import __version__ as version

long_description = 'Please see the documentation at the `project page <https://github.com/PGower/petl_ldap3>`_ .'

packages = [
    'petl_ldap3',
]

package_data = {
    '': ['LICENSE', 'README.md'],
}

setup(
    name='petl_ldap3',
    version=version,
    description='A petl view class for ldap data.',
    long_description=long_description,
    author='Paul Gower',
    author_email='p.gower@gmail.com',
    url='https://github.com/PGower/petl_ldap3',
    download_url='https://github.com/PGower/petl_ldap3/releases',
    package_dir={'petl_ldap3': 'petl_ldap3'},
    packages=packages,
    package_data=package_data,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['petl', 'ldap3'],
    install_requires=['ldap3', 'petl'],
)
