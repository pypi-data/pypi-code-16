"""
osxlaunch - Handle OSX launchd environment variables.

Provide tools to generate plist files for consumption by launchd to maintain
environment variables.
"""

import os
from setuptools import setup
import osxlaunch


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()


setup(
    name="osxlaunch",
    version=osxlaunch.get_version(),
    packages=['osxlaunch'],
    license='BSD License',
    description='Utility to working with OSX launchd environment variables.',
    long_description=README,
    url='https://github.com/zzzirk/osxlaunch',
    author='Louis Zirkel III',
    author_email='zzzirk@gmail.com',

    entry_points={
        'console_scripts': [
            'osxlaunch=osxlaunch.__main__:main',
        ],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Installation/Setup',
        'Topic :: Utilities',
    ],

)
