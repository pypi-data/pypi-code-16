##############################################################################
#
# Copyright (c) 2003, 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from setuptools import setup, find_packages


setup(
    name='zope.mkzeoinstance',
    version='4.0',
    url='https://github.com/zopefoundation/zope.mkzeoinstance',
    license='ZPL 2.1',
    description='Make standalone ZEO database server instances',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    long_description=(open('README.rst').read() + "\n" +
                      open('CHANGES.rst').read()),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords="ZEO ZODB instance script",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope'],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'zdaemon',
        'ZODB',    # not imported, but generated instance requires it
        'ZEO',     # not imported, but generated instance requires it
    ],
    zip_safe=False,
    test_suite='zope.mkzeoinstance.tests',
    entry_points={
        'console_scripts': [
            'mkzeoinstance = zope.mkzeoinstance:main',
        ],
    },
)
