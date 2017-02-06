# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='minetime',
    version='0.2.8',
    install_requires=['python-redmine', 'click', 'pyyaml', 'tabulate'],
    description='A simple Command line application helping you play with timelogs of configured redmine server.',
    long_description=readme,
    author='yakoi',
    author_email='jpgelinas@gmail.com',
    url='https://gitlab.com/yakoi/minetime',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'minetime=minetime.cli:mine_time',
        ],
    }
)
