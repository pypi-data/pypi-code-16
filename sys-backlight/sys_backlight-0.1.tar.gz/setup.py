#!/usr/bin/env python3

# Setup script for the `auto-adjust-display-brightness' package.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: November 18, 2015
# URL: https://github.com/xolox/python-auto-adjust-display-brightness

# Standard library modules.
import codecs
import os
import re

# De-facto standard solution for Python packaging.
from setuptools import setup, find_packages

# Find the directory where the source distribution was unpacked.
source_directory = os.path.dirname(os.path.abspath(__file__))

# Find the current version.
module = os.path.join(source_directory, 'sys_backlight', '__init__.py')
for line in open(module, 'r'):
    match = re.match(r'^__version__\s*=\s*["\']([^"\']+)["\']$', line)
    if match:
        version_string = match.group(1)
        break
else:
    raise Exception("Failed to extract version from %s!" % module)

# Fill in the long description (for the benefit of PyPI)
# with the contents of README.rst (rendered by GitHub).
readme_file = os.path.join(source_directory, 'README.rst')
with codecs.open(readme_file, 'r', 'utf-8') as handle:
    readme_text = handle.read()

setup(
    name='sys_backlight',
    version=version_string,
    description='Control linux screen brightness from commandline',
    url='https://github.com/hamgom95',
    author='Kevin Thomas',
    author_email='hamgom95@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
    ],
    package_data={
        'config': ['sys_backlight/config/backlight.ini']
    },
    entry_points=dict(console_scripts=[
        'backlight = sys_backlight:mode_console',
        'nbacklight = sys_backlight:mode_ncurses',
        'qbacklight = sys_backlight:mode_gui',
    ]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: Desktop Environment',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    keywords=["sys", "linux", "backlight"]
)
