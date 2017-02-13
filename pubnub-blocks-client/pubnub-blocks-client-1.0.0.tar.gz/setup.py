#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='pubnub-blocks-client',
    version='1.0.0',
    description='PubNub BLOCKS management.',
    long_description=('Package provide interface which allow to manage PubNub '
                      'BLOCKS infrastructure by providing the following '
                      'operations: create / remove, start / stop and rename '
                      'for blocks and create / modify / remove for event '
                      'handlers'),
    author='PubNub',
    author_email='support@pubnub.com',
    url='http://pubnub.com',
    download_url='https://github.com/pubnub/pubnub-blocks-client/tarball/1.0.0',
    keywords=('pubnub', 'blocks', 'event handlers', 'manage'),
    license='MIT',
    packages=find_packages(exclude=("examples*", 'tests*')),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later '
        '(GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ),
    install_requires=[
        'requests>=2.13',
        'six>=1.10'
    ],
    zip_safe=False
)
