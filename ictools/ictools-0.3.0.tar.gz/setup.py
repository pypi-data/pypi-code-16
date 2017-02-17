#!/usr/bin/env python
#

import setuptools

import ictools


def read_requirements(name):
    requirements = []
    with open(name) as req_file:
        for line in req_file:
            if '#' in line:
                line = line[:line.index('#')]
            line = line.strip()
            if line.startswith('-r'):
                requirements.extend(read_requirements(line[2:].strip()))
            elif line and not line.startswith('-'):
                requirements.append(line)
    return requirements

version = ictools.version
try:
    with open('LOCAL-VERSION') as version_file:
        version += version_file.readline().strip()
except IOError:
    pass

setuptools.setup(
    name='ictools',
    description='Incident Commander Utilities',
    version=version,
    long_description='\n'+open('README.rst').read(),
    url='https://github.com/dave-shawley/ictools',
    author='Dave Shawley',
    author_email='daves@aweber.com',
    packages=['ictools'],
    install_requires=read_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'scan-hipchat-room = ictools.hipchat:scan_room',
            'list-pagerduty-incidents = ictools.pagerduty:list_incidents',
            'create-confluence-table = ictools.io:combine_tables',
        ],
    },
    platforms='any',
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3',
                 'Development Status :: 4 - Beta'],
)
