#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='wizards',
    version='1.2.1',
    description='Wizards of Industry Common Library',
    author='Cochise Ruhulessin',
    author_email='cochiseruhulessin@gmail.com',
    url='https://www.wizardsofindustry.net',
    install_requires=[
        'werkzeug',
        'ea'
    ],
    packages=find_packages()
)
