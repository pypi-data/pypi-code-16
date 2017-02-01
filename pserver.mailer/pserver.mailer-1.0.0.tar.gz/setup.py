# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

setup(
    name='pserver.mailer',
    version=open('VERSION').read().strip(),
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGELOG.rst').read()),
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    keywords='async mail plone',
    license='BSD',
    zip_safe=True,
    author='Nathan Van Gheem',
    author_email='nathan.vangheem@wildcardcorp.com',
    url='https://github.com/pyrenees/pserver.mailer',
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['pserver'],
    install_requires=[
        'setuptools',
        'plone.server',
        'repoze.sendmail>=4.1',
        'transaction',
        'html2text',
        'aiosmtplib'
    ],
    tests_require=[
        'pytest',
    ],
    entry_points={
        'plone.server': [
            'include = pserver.mailer',
        ]
    }
)
