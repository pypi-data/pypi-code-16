"""Project metadata variables"""
NAME = 'pyprojectgen'
VERSION = '0.0.4'
DESCRIPTION = 'Generates python project structure.'
URL = 'https://github.com/mjalas/pyprojectgen'
AUTHOR = 'Mats Jalas'
AUTHOR_EMAIL = 'mats.jalas@gmail.com'
LICENSE = 'GNU GPLv3'
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
]
INSTALL_REQUIRES = [
    'PyYAML>=3.11'
]
SETUP_REQUIRES = [
    'nose>=1.0',
    'coverage>=4.0.3',
    'PyYAML>=3.11'
],
TESTS_REQUIRES = [
    'nose',
    'coverage>=4.0.3',
    'PyYAML'
]
