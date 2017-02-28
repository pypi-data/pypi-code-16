#!/usr/bin/env python
from setuptools import setup

setup(
    name='another_ping',
    version='0.1',
    description='Yet another ping module',
    url='',
    author='SgDylan',
    author_email='i@acg.works',
    install_requires = ['pexpect>=4.2.1'],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='ping python',
    packages=['another_ping'],
)