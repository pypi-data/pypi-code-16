#!/usr/bin/env python

from setuptools import setup

if __name__ == "__main__":

    with open('README.rst', 'r') as f:
        long_description = f.read()

    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()

    setup(
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: Implementation :: CPython',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
        name='cspark-python',
        description='Python library for Cisco Spark',
        long_description=long_description,
        version='0.0.12',
        author='Matvei Kukui',
        author_email='motakuk@gmail.com',
        url='https://github.com/Matvey-Kuk/cspark-python',
        packages=['cspark'],
        install_requires=requirements,
        package_data={'': ['requirements.txt']},
    )
